from typing import Literal

import boto3

from .._config import project_settings, settings


SES_SERVICE_NAME: Literal["ses"] = "ses"


class SESEmailService:
    def __init__(
        self,
        ses_client=None,
        from_email: str | None = None,
        project_name: str | None = None,
    ) -> None:
        self.ses_client = ses_client or boto3.client(
            service_name=SES_SERVICE_NAME,
            region_name=project_settings.aws_default_region,
            aws_access_key_id=settings.aws_access_key_id.get_secret_value()
            if settings.aws_access_key_id
            else None,
            aws_secret_access_key=settings.aws_secret_access_key.get_secret_value()
            if settings.aws_secret_access_key
            else None,
        )
        self.from_email = from_email or project_settings.from_email
        self.project_name = project_name or project_settings.project_name

    async def send_login_email(self, email: str, login_url: str):
        """Send login email using Amazon SES"""
        subject = f"Sign in to {self.project_name}"

        html_body = f"""
<html>
<body>
<h2>Sign in to {self.project_name}</h2>
<p>Click the link below to sign in to your account:</p>
<p><a href="{login_url}" style="background-color: #007bff; color: white; padding: 12px 24px; text-decoration: none; border-radius: 4px;">Sign In</a></p>
<p>This link will expire in 15 minutes.</p>
<p>If you didn't request this, you can safely ignore this email.</p>
</body>
</html>
"""

        text_body = f"""
Sign in to {self.project_name}

Copy and paste this link into your browser to sign in:
{login_url}

This link will expire in 15 minutes.
If you didn't request this, you can safely ignore this email.
"""

        response = self.ses_client.send_email(
            Source="no-reply@example.com",  # Replace with your verified SES email
            Destination={"ToAddresses": [email]},
            Message={
                "Subject": {"Data": subject, "Charset": "UTF-8"},
                "Body": {
                    "Text": {"Data": text_body, "Charset": "UTF-8"},
                    "Html": {"Data": html_body, "Charset": "UTF-8"},
                },
            },
        )
        return response
