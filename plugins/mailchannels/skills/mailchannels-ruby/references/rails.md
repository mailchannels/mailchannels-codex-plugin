# Rails and Ruby recipes for MailChannels

The delivery method below was tested on 2026-11-18 with Ruby 3.3, Action
Mailer 8.1, and `mailchannels-email-api` 0.1.0. The test replaced the gem's
HTTP call and checked the payload built for text-only, HTML-only, and
multipart mail with display names, cc, bcc, reply-to, a file attachment, and
an inline attachment. No live email was sent. Re-test against the versions the
project installs.

The gem requires Ruby 3.2 or later.

## Action Mailer delivery method

`Gemfile`:

```ruby
gem "mailchannels-email-api"
```

`lib/mailchannels_delivery.rb`:

```ruby
require "base64"
require "mailchannels/email_api"

# Action Mailer delivery method that submits mail through the MailChannels
# Email API with the mailchannels-email-api gem.
class MailchannelsDelivery
  class NotAccepted < StandardError; end

  attr_accessor :settings

  def initialize(settings = {})
    @settings = settings
  end

  def deliver!(mail)
    result = client.send_email(payload_for(mail))
    raise NotAccepted, "MailChannels returned HTTP #{result.status}" unless result.accepted?

    result
  end

  private

  def client
    MailChannels::EmailAPI::Client.new(
      api_key: settings[:api_key] || ENV["MAILCHANNELS_API_KEY"]
    )
  end

  def payload_for(mail)
    recipients = { to: addresses(mail[:to]) }
    recipients[:cc] = addresses(mail[:cc]) if mail[:cc]
    recipients[:bcc] = addresses(mail[:bcc]) if mail[:bcc]

    payload = {
      from: addresses(mail[:from]).first,
      personalizations: [recipients],
      subject: mail.subject.to_s,
      content: content_for(mail)
    }
    payload[:reply_to] = addresses(mail[:reply_to]).first if mail[:reply_to]
    files = mail.attachments.map { |file| attachment_for(file) }
    payload[:attachments] = files unless files.empty?
    payload
  end

  def addresses(field)
    field.addrs.map do |address|
      { email: address.address, name: address.display_name }.compact
    end
  end

  def content_for(mail)
    text = mail.text_part
    html = mail.html_part
    unless mail.multipart?
      html = mail if mail.mime_type == "text/html"
      text = mail unless html
    end

    parts = []
    parts << { type: "text/plain", value: text.decoded } if text
    parts << { type: "text/html", value: html.decoded } if html
    parts
  end

  def attachment_for(file)
    entry = {
      filename: file.filename,
      type: file.mime_type,
      content: Base64.strict_encode64(file.body.decoded)
    }
    entry[:content_id] = file.cid if file.inline?
    entry
  end
end
```

`config/initializers/mailchannels.rb`:

```ruby
require Rails.root.join("lib/mailchannels_delivery")

ActiveSupport.on_load(:action_mailer) do
  add_delivery_method :mailchannels, MailchannelsDelivery
end
```

`config/environments/production.rb`:

```ruby
config.action_mailer.delivery_method = :mailchannels
config.action_mailer.mailchannels_settings = {
  api_key: ENV.fetch("MAILCHANNELS_API_KEY")
}
```

Existing mailers need no change:

```ruby
UserMailer.with(user: user).password_reset.deliver_later
```

### What the delivery method does and does not do

- Maps `from`, `to`, `cc`, `bcc`, `reply_to`, `subject`, the text and HTML
  parts, and attachments, including inline attachments by content ID.
- Sends one message to all recipients. For per-recipient content, build
  `personalizations` and call the gem directly.
- Uses the first `from` and first `reply_to` address; the API takes one of
  each.
- Does not pass custom headers. Add a `headers:` hash to the payload if the
  app needs them; some headers are restricted
  ([custom headers](https://docs.mailchannels.com/email-api/custom-headers)).
- Calls `POST /send`. The gem has no `/send-async` method, so run deliveries
  in a background job.
- Raises `MailChannels::EmailAPI::APIError` (with `status`) for an unexpected
  HTTP status and `MailChannels::EmailAPI::TransportError` for a network
  failure. After a transport error the message may already have been
  accepted.

## Calling the gem directly

```ruby
require "mailchannels/email_api"

client = MailChannels::EmailAPI::Client.new # reads MAILCHANNELS_API_KEY
message = {
  from: { email: "notifications@example.com", name: "Example" },
  personalizations: [{ to: [{ email: "recipient@example.net" }] }],
  subject: "Your receipt",
  content: [{ type: "text/plain", value: "Thank you." }]
}

client.validate_email(message).validated? # dry run, sends nothing
client.send_email(message).accepted?      # HTTP 202
```

Payloads use the API's JSON field names without conversion.

## SMTP

```ruby
config.action_mailer.delivery_method = :smtp
config.action_mailer.smtp_settings = {
  address: "smtp.mailchannels.net",
  port: 587,
  user_name: ENV.fetch("MAILCHANNELS_ACCOUNT_ID"),
  password: ENV.fetch("MAILCHANNELS_SMTP_PASSWORD"),
  enable_starttls: true
}
```

The username is the MailChannels account ID and the password is an SMTP
password created in the dashboard. Domain Lockdown and SPF records are
required for SMTP too. Messages sent this way are not DKIM-signed by
MailChannels and produce no delivery webhooks; sign in the app if DKIM is
needed.

## Everything else over REST

Queued sending (`POST /send-async`), webhook enrollment, suppressions, DKIM
keys, the domain check, and metrics have no Ruby wrapper. Call them with
`Net::HTTP` using the `X-Api-Key` header against
`https://api.mailchannels.net/tx/v1`; the `mailchannels-rest` skill has the
request shapes.
