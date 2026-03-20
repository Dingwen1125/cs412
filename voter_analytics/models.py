# File: models.py
# Author: Dingwen Yang (laoba@bu.edu), 3/19/2026
# Description: Django model and data-loading function for the
# voter analytics application.

from django.db import models

class Voter(models.Model):
    last_name = models.TextField()
    first_name = models.TextField()
    street_num = models.IntegerField()
    street_name = models.TextField()
    apartment_num = models.CharField(max_length=20, blank=True)
    zip_code = models.CharField(max_length=10)
    date_of_birth = models.DateField()
    date_of_registration = models.DateField()
    party_affiliation = models.CharField(max_length=2)
    precinct_number = models.CharField(max_length=10)

    v20state = models.BooleanField()
    v21town = models.BooleanField()
    v21primary = models.BooleanField()
    v22general = models.BooleanField()
    v23town = models.BooleanField()

    voter_score = models.IntegerField()

    def __str__(self):
        return f'{self.first_name} {self.last_name} ({self.street_num} {self.street_name})'

def load_data():
    """Load voter records from the CSV file into the Voter model table."""

    Voter.objects.all().delete()
    filename = 'newton_voters.csv'
    f = open(filename)
    f.readline() # discard headers

    for line in f:
        fields = line.split(',')

        # Skip malformed rows so that one bad record does not stop the full import.
        try:
            voter = Voter(last_name = fields[1],
                          first_name = fields[2],
                          street_num = fields[3],
                          street_name = fields[4],
                          apartment_num = fields[5],
                          zip_code = fields[6],
                          date_of_birth = fields[7],
                          date_of_registration = fields[8],
                          party_affiliation = fields[9].strip(),
                          precinct_number = fields[10],
                          v20state = (fields[11] == 'TRUE'),
                          v21town = (fields[12] == 'TRUE'),
                          v21primary = (fields[13] == 'TRUE'),
                          v22general = (fields[14] == 'TRUE'),
                          v23town = (fields[15] == 'TRUE'),
                          voter_score = int(fields[16].strip()),)
            voter.save()
        except:
            print(f"Skipped: {fields}")

    print(f'Done. Created {len(Voter.objects.all())} Results.')
