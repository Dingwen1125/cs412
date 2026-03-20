# File: views.py
# Author: Dingwen Yang (laoba@bu.edu), 3/19/2026
# Description: Django views for listing, filtering, graphing,
# and showing detail pages for voter records.

from django.shortcuts import render
from django.db.models import Count
from django.db.models.query import QuerySet
from django.shortcuts import render
from django.views.generic import ListView, DetailView
from django.views.generic import ListView
from urllib.parse import quote_plus

import plotly
import plotly.graph_objs as go

from .models import Voter


class VotersListView(ListView):
    """Display the full voter list and allow filtering by form input."""

    template_name = "voter_analytics/results.html"
    model = Voter
    context_object_name = 'voters'

    def get_queryset(self):
        """Return the voter records after applying any selected filters."""
        voters = super().get_queryset().order_by('last_name', 'first_name')

        # Read the current search form values from the URL query string.
        party = self.request.GET.get('party_affiliation')
        min_year = self.request.GET.get('min_birth_year')
        max_year = self.request.GET.get('max_birth_year')
        voter_score = self.request.GET.get('voter_score')

        # Apply each optional filter only when the user selected a value.
        if party:
            voters = voters.filter(party_affiliation=party)
        if min_year:
            voters = voters.filter(date_of_birth__year__gte=min_year)
        if max_year:
            voters = voters.filter(date_of_birth__year__lte=max_year)
        if voter_score:
            voters = voters.filter(voter_score=voter_score)

        # Keep only voters who participated in any checked election boxes.
        for election_field in ['v20state', 'v21town', 'v21primary', 'v22general', 'v23town']:
            if self.request.GET.get(election_field):
                voters = voters.filter(**{election_field: True})
        return voters

    def get_context_data(self, **kwargs):
        """Add dropdown options needed by the reusable search form."""
        context = super().get_context_data(**kwargs)

        voters = Voter.objects.all()
        context['party_choices'] = voters.order_by().values_list(
            'party_affiliation', flat=True).distinct().order_by('party_affiliation')
        context['birth_years'] = voters.dates('date_of_birth', 'year', order='ASC')
        context['score_choices'] = voters.order_by().values_list(
            'voter_score', flat=True).distinct().order_by('voter_score')
        return context


class VoterDetailView(DetailView):
    """Display the detail page for one voter and build a Google Maps link."""

    template_name = "voter_analytics/voter_detail.html"
    model = Voter
    context_object_name = 'voter'

    def get_context_data(self, **kwargs):
        """Add the Google Maps URL for the selected voter's address."""
        context = super().get_context_data(**kwargs)
        voter = context['voter']
        address = f"{voter.street_num} {voter.street_name} {voter.apartment_num} {voter.zip_code}"
        context['google_maps_url'] = f"https://www.google.com/maps/search/?api=1&query={quote_plus(address)}"
        return context


class GraphsListView(ListView):
    """Display plotly graphs summarizing the filtered voter records."""

    template_name = "voter_analytics/graphs.html"
    model = Voter
    context_object_name = 'voters'

    def get_queryset(self):
        """Return the voter records after applying graph page filters."""
        voters = super().get_queryset().order_by('last_name', 'first_name')

        # Read the current search form values from the URL query string.
        party = self.request.GET.get('party_affiliation')
        min_year = self.request.GET.get('min_birth_year')
        max_year = self.request.GET.get('max_birth_year')
        voter_score = self.request.GET.get('voter_score')

        # Apply each optional filter only when the user selected a value.
        if party:
            voters = voters.filter(party_affiliation=party)
        if min_year:
            voters = voters.filter(date_of_birth__year__gte=min_year)
        if max_year:
            voters = voters.filter(date_of_birth__year__lte=max_year)
        if voter_score:
            voters = voters.filter(voter_score=voter_score)

        # Keep only voters who participated in any checked election boxes.
        for election_field in ['v20state', 'v21town', 'v21primary', 'v22general', 'v23town']:
            if self.request.GET.get(election_field):
                voters = voters.filter(**{election_field: True})
        return voters

    def get_context_data(self, **kwargs):
        """Build the aggregate plotly graphs for the filtered voters."""
        context = super().get_context_data(**kwargs)

        # Provide the same dropdown options used on the list page search form.
        all_voters = Voter.objects.all()
        context['party_choices'] = all_voters.order_by().values_list(
            'party_affiliation', flat=True).distinct().order_by('party_affiliation')
        context['birth_years'] = all_voters.dates('date_of_birth', 'year', order='ASC')
        context['score_choices'] = all_voters.order_by().values_list(
            'voter_score', flat=True).distinct().order_by('voter_score')
        voters = self.get_queryset()

        # Aggregate the filtered voters into counts used by the three graphs.
        birth_year_data = voters.values('date_of_birth__year').annotate(total=Count('id')).order_by('date_of_birth__year')
        party_data = voters.values('party_affiliation').annotate(total=Count('id')).order_by('party_affiliation')

        # Create the required bar chart and pie chart visualizations.
        birth_year_fig = go.Bar(
            x=[item['date_of_birth__year'] for item in birth_year_data],
            y=[item['total'] for item in birth_year_data],
        )
        party_fig = go.Pie(
            labels=[item['party_affiliation'] for item in party_data],
            values=[item['total'] for item in party_data],
        )
        election_fig = go.Bar(
            x=['v20state', 'v21town', 'v21primary', 'v22general', 'v23town'],
            y=[
                voters.filter(v20state=True).count(),
                voters.filter(v21town=True).count(),
                voters.filter(v21primary=True).count(),
                voters.filter(v22general=True).count(),
                voters.filter(v23town=True).count(),
            ],
        )

        # Convert each plotly figure into an HTML div for the template.
        context['graph_div_birth_year'] = plotly.offline.plot(
            {"data": [birth_year_fig], "layout_title_text": "Distribution of Voters by Year of Birth"},
            auto_open=False,
            output_type="div",
        )
        context['graph_div_party'] = plotly.offline.plot(
            {"data": [party_fig], "layout_title_text": "Distribution of Voters by Party Affiliation"},
            auto_open=False,
            output_type="div",
        )
        context['graph_div_elections'] = plotly.offline.plot(
            {"data": [election_fig], "layout_title_text": "Distribution of Voters by Participation in Each Election"},
            auto_open=False,
            output_type="div",
        )
        return context
