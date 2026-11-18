# Ruby and Rails with MailChannels Email API

MailChannels publishes official SDKs for JavaScript, Python, and PHP only
([official libraries](https://docs.mailchannels.com/email-api/official-libraries)).
There is no official Ruby SDK and no packaged Action Mailer delivery method.
Ruby apps have three honest options:

| Option | DKIM signing by MailChannels | Delivery webhooks | Notes |
|---|---|---|---|
| REST API from a small Action Mailer delivery method (below) | Yes | Yes | Keeps existing mailers, views, and `deliver_later` |
| Action Mailer's built-in `:smtp` delivery to `smtp.mailchannels.net:587` | No | No | No code; your own DKIM signatures pass through intact |
| [`mailchannels-email-api`](https://rubygems.org/gems/mailchannels-email-api) gem | Yes (REST) | Yes (REST) | API client gem, version 0.1.0; not one of the documented official SDKs and not a delivery method |

Every option needs the same account setup: an API key (or SMTP password),
a Domain Lockdown TXT record and SPF include for each sending domain, and DKIM
before production ([quickstart](https://docs.mailchannels.com/email-api/curl/quickstart)).

## Action Mailer delivery method over REST

Action Mailer accepts any class with `initialize(settings)` and
`deliver!(mail)`. This one uses only the Ruby standard library and posts to
`POST https://api.mailchannels.net/tx/v1/send` with the `X-Api-Key` header.

```ruby
# lib/mailchannels_delivery.rb
require "base64"
require "json"
require "net/http"
require "uri"

class MailchannelsDelivery
  class Error < StandardError
    attr_reader :status

    def initialize(status, body)
      @status = status
      super("MailChannels send failed with HTTP #{status}: #{body.to_s[0, 500]}")
    end

    # 500 and 502 are transient; 400, 403 and 413 need a corrected request.
    def retryable?
      status >= 500
    end
  end

  DEFAULT_URL = "https://api.mailchannels.net/tx/v1/send"

  attr_accessor :settings

  def initialize(settings)
    @settings = { url: DEFAULT_URL, open_timeout: 5, read_timeout: 30 }.merge(settings)
    raise ArgumentError, "MailChannels api_key is required" if @settings[:api_key].to_s.empty?
  end

  def deliver!(mail)
    uri = URI(settings[:url])
    request = Net::HTTP::Post.new(uri)
    request["Content-Type"] = "application/json"
    request["X-Api-Key"] = settings[:api_key]
    request.body = JSON.generate(payload(mail))

    response = Net::HTTP.start(uri.host, uri.port, use_ssl: uri.scheme == "https",
                               open_timeout: settings[:open_timeout],
                               read_timeout: settings[:read_timeout]) do |http|
      http.request(request)
    end
    raise Error.new(response.code.to_i, response.body) unless response.is_a?(Net::HTTPSuccess)

    body = response.body.to_s.empty? ? {} : JSON.parse(response.body)
    mail["X-MailChannels-Request-Id"] = body["request_id"] if body["request_id"]
    body
  end

  private

  def payload(mail)
    from = addresses(mail[:from]).first or raise ArgumentError, "mail has no From address"
    personalization = { to: addresses(mail[:to]) }
    personalization[:cc] = addresses(mail[:cc]) if mail.cc
    personalization[:bcc] = addresses(mail[:bcc]) if mail.bcc

    body = {
      personalizations: [personalization],
      from: from,
      subject: mail.subject.to_s,
      content: content(mail)
    }
    reply_to = addresses(mail[:reply_to]).first
    body[:reply_to] = reply_to if reply_to
    attachments = mail.attachments.map do |part|
      { filename: part.filename, type: part.mime_type,
        content: Base64.strict_encode64(part.decoded) }
    end
    body[:attachments] = attachments unless attachments.empty?
    body
  end

  def addresses(field)
    return [] unless field

    field.addrs.map do |address|
      entry = { email: address.address }
      entry[:name] = address.display_name if address.display_name
      entry
    end
  end

  def content(mail)
    text = mail.multipart? ? mail.text_part : (mail.mime_type == "text/html" ? nil : mail)
    html = mail.multipart? ? mail.html_part : (mail.mime_type == "text/html" ? mail : nil)
    parts = []
    parts << { type: "text/plain", value: text.decoded } if text
    parts << { type: "text/html", value: html.decoded } if html
    parts
  end
end
```

Register it and select it per environment:

```ruby
# config/initializers/mailchannels.rb
require Rails.root.join("lib/mailchannels_delivery")

ActionMailer::Base.add_delivery_method :mailchannels, MailchannelsDelivery,
  api_key: ENV.fetch("MAILCHANNELS_API_KEY", "")

# config/environments/production.rb
config.action_mailer.delivery_method = :mailchannels
config.action_mailer.raise_delivery_errors = true
```

Keep `:test` delivery in the test environment so ordinary tests never call
the API. To check rendering against the real API without sending, point `url`
at `https://api.mailchannels.net/tx/v1/send?dry-run=true`, which returns the
rendered message instead of sending it.

### Retries and duplicates

The API has no idempotency key. With `deliver_later`, Active Job retries a
failed job, so only let it retry `MailchannelsDelivery::Error` when
`retryable?` is true, and treat a network timeout as ambiguous: the message
may already have been accepted. For mail that must never duplicate (password
resets, receipts), record a unique key per logical email before enqueueing and
skip the send when that key is already marked sent.

## SMTP alternative

```ruby
config.action_mailer.delivery_method = :smtp
config.action_mailer.smtp_settings = {
  address: "smtp.mailchannels.net",
  port: 587,
  user_name: ENV.fetch("MAILCHANNELS_ACCOUNT_ID"),
  password: ENV.fetch("MAILCHANNELS_SMTP_PASSWORD"),
  authentication: :plain,
  enable_starttls_auto: true
}
```

SMTP uses the account ID as the username and an SMTP password from the
dashboard or API ([SMTP](https://docs.mailchannels.com/email-api/smtp-sending)).
MailChannels does not DKIM-sign SMTP mail and SMTP sends produce no delivery
webhooks, so choose the REST delivery method when either matters.

## Scope

The Email API sends outbound mail only. Action Mailbox or any other inbound
processing needs a separate receiving service; MailChannels webhooks report
delivery events, not inbound messages.
