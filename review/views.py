from django.shortcuts import render, get_object_or_404
from django.forms.models import model_to_dict
from publication.models import Publication
from .models import Review, ReviewSite, ReviewInterval

# Create your views here.

def become_reviewer(request):
    # 1. check privilege
    # 1. check privilege
    # 1. check privilege
    # 1. check privilege
    # 1. check privilege
    return render()

def nominate(request):
    """Accepts an incoming nomination from a reviewer to review a particular publication"""
    
    # 1. Create a review object 
    review = Review()

    # 2. Retrieve the publication and add to review object
    pub_pk = request.GET.get('publication')
    if pub_pk:
        pub = get_object_or_404(Publication, pub_pk)
    review.publication = pub

    # 3. Get related sites and copy to review table
    for site in pub.sites.all():
        values = model_to_dict(site)
        refs = values.pop('references')
        s = ReviewSite(**values)
        s.save()
        s.references.add(*refs)

    # 4. Get related intervals and copy to review tables
    for i in pub.intervals.all():
        values = model_to_dict(i)
        site = values.pop('site')
        refs = values.pop('reference')
        corrs = values.pop('corrections')
        s = ReviewInterval(**values,
        site=ReviewSite.objects.get(id=site),
        reference=pub)
        s.save()
        s.corrections.add(*corrs)


    # 5. Add review site and intervals to Review object

    return render()

def submit(request):
    """Allows a reviewer to submit their revised data for acceptance by site admins"""
    return render()

def accept(request):
    """Allows a site admin to accept a review as complete and copy the data back across to the main database"""
    return render()