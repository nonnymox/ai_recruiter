from django.db import models

class CandidateRanking(models.Model):
    fullname = models.CharField(max_length=255)
    email = models.EmailField()
    score = models.IntegerField()
    resume_link = models.TextField()
    screening_q1 = models.TextField()
    screening_q2 = models.TextField()
    screening_q3 = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.fullname} - {self.score}"
