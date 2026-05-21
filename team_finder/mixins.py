from urllib.parse import urlparse

from django import forms


class GithubUrlMixin:
    def clean_github_url(self):
        url = (self.cleaned_data.get("github_url") or "").strip()
        if not url:
            return url
        parsed = urlparse(url)
        if not parsed.scheme or "github.com" not in parsed.netloc:
            raise forms.ValidationError("Ссылка должна вести на GitHub (github.com)")
        return url
