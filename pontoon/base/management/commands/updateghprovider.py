# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

# This file has been copied from http://github.com/mozilla/testpilot
# and has been modified in order to use Fxa provider from the allauth package.
from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand
from django.conf import settings
from django.contrib.sites.models import Site
from allauth.socialaccount.models import SocialApp
from allauth.socialaccount.providers.github.provider import GitHubProvider


GITHUB_PROVIDER_ID = GitHubProvider.id


class Command(BaseCommand):
    help = ('Ensures an allauth application for Github OAuth exists and has '
            'credentials that match settings')

    def handle(self, *args, **options):
        # Check if GITHUB_* settings are configured, bail if not.
        if settings.GITHUB_CLIENT_ID is None or settings.GITHUB_SECRET_KEY is None:
            self.stdout.write("GITHUB_* settings unavailable; "
                              "skipping provider config.")
            return

        # Grab the credentials from settings
        data = dict(
            name='github',
            provider=GITHUB_PROVIDER_ID,
            client_id=settings.GITHUB_CLIENT_ID,
            secret=settings.GITHUB_SECRET_KEY
        )

        try:
            # Update the existing provider with current settings.
            app = SocialApp.objects.get(provider=GITHUB_PROVIDER_ID)
            self.stdout.write("Updating existing Github OAuth provider "
                              "(pk=%s)" % app.pk)
            for k, v in data.items():
                setattr(app, k, v)
            app.save()
        except ObjectDoesNotExist:
            # Create the provider if necessary.
            app = SocialApp(**data)
            app.save()
            self.stdout.write("Created new Github OAuth provider (pk=%s)" %
                              app.pk)

        # Ensure the provider applies to the current default site.
        sites_count = app.sites.count()
        if sites_count == 0:
            default_site = Site.objects.get(pk=settings.SITE_ID)
            app.sites.add(default_site)
