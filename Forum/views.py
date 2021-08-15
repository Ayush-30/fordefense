from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.http import HttpResponse
# Create your views here.
import re

from django.contrib.auth.views import login_required
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.generic import UpdateView, DeleteView
from sklearn.preprocessing import MinMaxScaler

from scipy.sparse import csr_matrix
from .models import *
from user.models import Profile
from user.form import Userupdateform,Userprofileupdate
from datetime import datetime, timedelta
import pandas as pd
from sklearn.neighbors import NearestNeighbors
from django.utils.crypto import get_random_string
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import sigmoid_kernel
from sklearn.decomposition import PCA
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.metrics.pairwise import linear_kernel
import json


@login_required
def forum(request):
    user = request.user
    user_sem = Profile.objects.get(user=user)
    u_form = Userupdateform(instance=request.user)
    questions = QuestionPost.objects.filter(question_author_semester=user_sem.semester)
    paginator = Paginator(questions, 10)
    try:
        page = int(request.GET.get('page', '1'))
    except:
        page = 1
    questions = paginator.get_page(page)
    context = {'u_form': u_form, 'q': questions,'user':user}
    return render(request, 'forum/dashboard.html', context)

@login_required
def tsort(request):
    u = request.user
    user_sem = Profile.objects.get(user=u)
    q = QuestionPost.objects.filter(question_author_semester=user_sem.semester)
    one_week_ago = datetime.today() - timedelta(days=7)
    questions = q.filter(date_posted__gte=one_week_ago).order_by('-question_answer_count')
    paginator = Paginator(questions, 10)
    try:
        page = int(request.GET.get('page', '1'))
    except:
        page = 1
    questions = paginator.get_page(page)
    context = {'q': questions}
    return render(request, 'forum/treanding.html', context)


@login_required
def rsort(request):
    u = request.user
    user_sem = Profile.objects.get(user=u)
    q = QuestionPost.objects.filter(question_author_semester=user_sem.semester)
    questions= q.order_by('-date_posted')
    paginator = Paginator(questions, 10)
    try:
        page = int(request.GET.get('page', '1'))
    except:
        page = 1
    questions = paginator.get_page(page)
    context = {'q': questions}
    return render(request, 'forum/latest.html', context)

@login_required
def msort(request):
    u = request.user
    user_sem = Profile.objects.get(user=u)
    q = QuestionPost.objects.filter(question_author_semester=user_sem.semester)
    questions = q.order_by('-question_view_count')
    paginator = Paginator(questions, 10)
    try:
        page = int(request.GET.get('page', '1'))
    except:
        page = 1
    questions = paginator.get_page(page)
    context = {'q': questions}
    return render(request, 'forum/mostviewed.html', context)



def newquestion(request):
    if request.method == 'POST':
        question = request.POST.get('question_content')
        if QuestionPost.objects.filter(question_content=question).exists():
            messages.info(request, 'Question already exists.')
            return redirect('newquestion')
        q = QuestionPost()
        q.question_content = question
        q.question_subject = request.POST.get('question_subject')
        q.posted_by = request.user
        q.question_author_semester = request.POST.get('question_author_semester')
        q.save()
        c = Profile.objects.get(user=q.posted_by)
        post_count = QuestionPost.objects.filter(posted_by=q.posted_by).count()
        c.number_of_posts = post_count
        c.save()
        return redirect(viewquestion, q.id)
    else:
        user = request.user
        user_sem = Profile.objects.get(user=user)
        messages.info(request,"Question already exist")
        content = {
            'u_form': user_sem,

        }
        return render(request, 'forum/addquestion.html', content)


def viewquestion(request, question_id):
    context = {}
    question = QuestionPost.objects.filter(pk=question_id)
    view_count = QuestionPost.objects.get(pk=question_id)
    view_count.question_view_count = view_count.question_view_count + 1
    view_count.save()

    if request.method == 'POST':
        a = AnswerPost()
        a.answer_text = request.POST.get('answer_text')
        a.question_id = question_id
        a.posted_by = request.user
        a.save()

    q = QuestionPost.objects.get(pk=question_id)
    qcount = AnswerPost.objects.filter(question_id=question_id).count()
    q.question_answer_count = qcount
    q.save()

    answers = AnswerPost.objects.filter(question_id=question_id)
    paginator = Paginator(answers, 10)
    try:
        page = int(request.GET.get('page', '1'))
    except:
        page = 1
    answers = paginator.get_page(page)

    context = {}
    question = QuestionPost.objects.filter(pk=question_id)
    for q in question:
        a = str(q.question_content)
        b = str(q.question_subject)
    a.replace(' ', '')


    recom = pd.DataFrame(list(
        QuestionPost.objects.all().values('question_view_count', 'question_content', 'question_answer_count','question_subject',
                                          'posted_by', 'id', 'question_like', 'posted_by_id')))
    scaling = MinMaxScaler()
    recom_scaled_df = scaling.fit_transform(recom[['question_view_count', 'question_answer_count']])
    recom_normalized_df = pd.DataFrame(recom_scaled_df, columns=['question_view_count', 'question_answer_count'])
    recom[['NQuestion View Count', 'NQuestion Answer Count']] = recom_normalized_df
    recom['score'] = recom['NQuestion View Count'] * 0.5 + recom['NQuestion Answer Count'] * 0.5
    recom = recom.sort_values(['score'], ascending=False)
    print(recom)
    # test = recom.sort_values(['score'], ascending=[False])
    # print(test)
    recom.rename(columns={'question_view_count': 'QuestionViewCount'}, inplace=True)
    recom = recom.drop_duplicates(['id', 'question_content'])

    recom_pivot = recom.pivot(index='id', columns='question_content', values='score')
    recom_pivot.fillna(0, inplace=True)
    # print(recom_pivot)
    recom_matrix = csr_matrix(recom_pivot.values)
    # print(recom_matrix)
    recom_pivot.reset_index(inplace=True)
    model_knn = NearestNeighbors(metric='cosine', algorithm='brute')
    model_knn.fit(recom_matrix)
    n_question_to_reccomend = 100

    # for i in a:
    #     if i == "(":
    #         a = question_list = recom[recom['question_content'].str.contains('|'.join(a), regex=True)]
    #     elif i == ")":
    #         a = question_list = recom[recom['question_content'].str.contains('|'.join(a), regex=True)]
    #     elif i == "?":
    #         a = question_list = recom[recom['question_content'].str.contains('|'.join(a), regex=True)]
    #     else:
    question_list = recom[recom['question_content'].str.contains(a)]
    if len(question_list):
        question_idx = question_list.iloc[0]['id']
        question_idx = recom_pivot[recom_pivot['id'] == question_idx].index[0]
        distances, indices = model_knn.kneighbors(recom_matrix[question_idx], n_neighbors=n_question_to_reccomend + 1)
        rec_question_indices = sorted(list(zip(indices.squeeze().tolist(), distances.squeeze().tolist())),
                                   key=lambda x: x[1])[:0:-1]
        print(indices)
        recommend_frame = []
        for val in rec_question_indices:
            question_idx = recom_pivot.iloc[val[0]]['id']
            idx = recom[recom['id'] == question_idx].index
            recommend_frame.append({'Title': recom.iloc[idx]['question_content'].values[0], 'question_subject': recom.iloc[idx]['question_subject'].values[0], 'Distance': val[1], 'id':  recom.iloc[idx]['id'].values[0]})
            print(idx)
        df = pd.DataFrame(recommend_frame, index=range(1, n_question_to_reccomend + 1))
        # print(df)
        popularity_threshold = b
        df = df.query('question_subject == @popularity_threshold')
        df.sort_values('Distance', ascending=False, inplace=True)
        output = df[1:].head(8)
        json_record = output.reset_index().to_json(orient='records')
        data = json.loads(json_record)
        context = {'question': question, 'q': data, 'answers': answers}
        print(context)

    return render(request, "forum/error.html", context)



def myposts(request):
    q = QuestionPost.objects.filter(posted_by=request.user)

    paginator = Paginator(q, 5)
    try:
        page = int(request.GET.get('page', '1'))
    except:
        page = 1
    q = paginator.get_page(page)
    return render(request, 'forum/myposts.html', {'q': q})


def UserPostListView(request, username):
    m = User.objects.get(username=username)
    q = QuestionPost.objects.filter(posted_by=m)
    user = request.user
    if str(user) != str(username):
        paginator = Paginator(q, 5)
        try:
            page = int(request.GET.get('page', '1'))
        except:
            page = 1
        q = paginator.get_page(page)
        return render(request, 'forum/dashboard.html', {'q': q})
    else:
        u_form = Userupdateform(user)
        content = {
            'u_form': u_form,
        }
        return render(request, 'user/profile.html', content)


def search1(request):
    query = request.GET['searchquery']
    if len(query) == 0:
        messages.info(request, 'Please fill something. Empty Search')
        content = {'q': query}
        return render(request, 'forum/search.html', content)
    elif len(query) >= 150:
        messages.info(request, 'Search query is too long')
        # return redirect(forum)
        # content = {'q': query}
        return render(request, 'forum/search.html')
    elif len(query) == 100:
        content = {}
        question = []
        content = {'q': question}
        return render(request, 'user/search.html', content)
    else:
        allposttitle = QuestionPost.objects.filter(Q(question_content__icontains=query) | Q(question_author_semester__icontains=query))
        allpostauthorsem = QuestionPost.objects.filter(Q(posted_by__username__icontains=query))
        allpostsubject = QuestionPost.objects.filter(Q(question_subject__icontains=query))
        question = allposttitle.union(allpostauthorsem, allpostsubject)
        paginator = Paginator(question, 5)
        try:
            page = int(request.GET.get('page', '1'))
        except:
            page = 1
        question = paginator.get_page(page)
        content = {'q': question,
                   'query': query}
        return render(request, 'forum/search.html', content)


def like_question(request, question_id):
    user = request.user
    # if request.method == 'POST':
    post = get_object_or_404(QuestionPost, pk=question_id)
    #     # post = AnswerPost.objects.get(answer_id=request.POST.get('answer_id'))
    s = QuestionPost.objects.get(pk=post.question_id)
    if user in post.question_like.all():
            post.question_like.remove(user)
            post.save()
    else:
            post.question_like.add(user)
            post.save()

    like, created = QuestionLike.objects.get_or_create(user=user, post=post)

    if not created:
            if like.value == 'Like':
                like.value == 'Unlike'
            else:
                like.value == 'Like'
    like.save()
    return redirect(viewquestion, post.question_id)



def like_post(request, answer_id):
    user = request.user
    # if request.method == 'POST':
    post = get_object_or_404(AnswerPost, answer_id=answer_id)
    #     # post = AnswerPost.objects.get(answer_id=request.POST.get('answer_id'))
    s = QuestionPost.objects.get(pk=post.question_id)
    if user in post.liked.all():
            post.liked.remove(user)
            post.save()
    else:
            post.liked.add(user)
            post.save()

    like, created = AnswerLike.objects.get_or_create(user=user, post=post)

    if not created:
            if like.value == 'Like':
                like.value == 'Unlike'
            else:
                like.value == 'Like'
    like.save()
    return redirect(viewquestion, post.question_id)

    # content = {'post': post}
    # return render(request, 'forum/user_profile_display.html', content)
    # return HttpResponseRedirect(AnswerPost.get_absolute_url(self=AnswerPost))


def notification(request):
    user = request.user
    notification = SendNotification.objects.filter(user=user)
    notification.update(viewed=True)

    paginator = Paginator(notification, 5)
    page = request.GET.get("page")
    try:
        query_list = paginator.page(page)
    except PageNotAnInteger:
        query_list = paginator.page(1)
    except EmptyPage:
        query_list = paginator.page(paginator.num_pages)

    context = {"query_list": query_list}
    return render(request, "forum/notification.html", context)

@login_required
def questionupdate(request, question_id):
    contexts = {}
    contents = QuestionPost.objects.get(pk=question_id)
    if contents.posted_by == request.user:
        if request.method == 'POST':
            # QuestionPost.objects.filter(id=question_id).update(question_content=data['ques'], phone=data['phone'])
            question_content = request.POST.get('question_content')
            # question_subject = request.POST.get('question_subject')
            q = QuestionPost()
            q.pk = question_id
            q.question_content = question_content
            q.question_subject = request.POST.get('question_subject')
            q.posted_by = request.user
            sem = Profile.objects.get(user=q.posted_by)
            q.question_author_semester = sem.semester
            q.save(update_fields=["question_content", "question_subject"])
            return redirect(viewquestion, q.question_id)
        else:
            user = request.user
            user_sem = Profile.objects.get(user=user)

            content = {
                'u_form': user_sem,
                'q': contents,
            }
            return render(request, 'forum/updatequestion.html', content)


def answerdelete(request, answer_id):
    content = AnswerPost.objects.get(pk=answer_id)
    if content.posted_by == request.user:
        content.delete()
    else:
        messages.info(request, 'Sorry, you are not authenticated to delete this comment')
    return redirect(viewquestion, content.question_id)


@login_required
def user_profile_display(request, question_id):
    content = QuestionPost.objects.get(pk=question_id)
    if request.user == content.posted_by:
        u_form = Userupdateform(instance=content.posted_by)
        content = {
            'u_form': u_form,
        }
        return render(request, 'user/profile.html', content)
    else:
        # u_form = Userupdateform(instance=content.posted_by)
        u = User.objects.filter(username=content.posted_by)
        print(u)
        m = User.objects.get(username=content.posted_by)
        q = QuestionPost.objects.filter(posted_by=m)
        content = {'u': u, 'q': q}
        return render(request, 'forum/user_profile_display.html', content)




# def test(request, question_id):
    #         context = {}
    #         question = QuestionPost.objects.filter(pk=question_id)
    #         for q in question:
    #             a = str(q.question_content)
    #         # a = question.objects.filter(question_content=question_content)
    #         # content['question'] = question
    #         # a = content.question_content
    # # if request.method == 'POST':
    # #     if request.POST.get('searchname'):
    # #         a = request.POST.get('searchname')
    # #         print(a)
    #         recom = pd.DataFrame(list(QuestionPost.objects.all().values('question_view_count','question_content','question_answer_count','posted_by','id','question_like','posted_by_id')))
    #         scaling = MinMaxScaler()
    #         recom_scaled_df = scaling.fit_transform(recom[['question_view_count', 'question_answer_count']])
    #         recom_normalized_df = pd.DataFrame(recom_scaled_df,columns=['question_view_count', 'question_answer_count'])
    #         recom[['NQuestion View Count', 'NQuestion Answer Count']] = recom_normalized_df
    #         recom['score'] = recom['NQuestion View Count'] * 0.5 + recom['NQuestion Answer Count'] * 0.5
    #         recom = recom.sort_values(['score'], ascending=False)
    #         print(recom)
    #         test = recom.sort_values(['score'], ascending=[False])
    #         print(test)
    #         recom.rename(columns={'question_view_count': 'QuestionViewCount'}, inplace=True)
    #         recom = recom.drop_duplicates(['id','question_content'])
    #         recom_pivot = recom.pivot(index='id', columns='question_content', values='score')
    #         recom_pivot.fillna(0, inplace=True)
    #         print(recom_pivot)
    #         recom_matrix = csr_matrix(recom_pivot.values)
    #         recom_pivot.reset_index(inplace=True)
    #         model_knn = NearestNeighbors(metric='cosine', algorithm='brute')
    #         model_knn.fit(recom_matrix)
    #         data = []
    #         new = []
    #
    #
    #         # def get_movie_recommendation(movie_name):
    #         n_movies_to_reccomend = 20
    #         movie_list = recom[recom['question_content'].str.contains(a)]
    #         if len(movie_list):
    #                 movie_idx = movie_list.iloc[0]['id']
    #                 movie_idx = recom_pivot[recom_pivot['id'] == movie_idx].index[0]
    #                 distances, indices = model_knn.kneighbors(recom_matrix[movie_idx], n_neighbors=n_movies_to_reccomend + 1)
    #                 rec_movie_indices = sorted(list(zip(indices.squeeze().tolist(), distances.squeeze().tolist())),
    #                                            key=lambda x: x[1])[:0:-1]
    #                 print(indices)
    #                 recommend_frame = []
    #                 for val in rec_movie_indices:
    #                     movie_idx = recom_pivot.iloc[val[0]]['id']
    #                     idx = recom[recom['id'] == movie_idx].index
    #                     recommend_frame.append({'Title': recom.iloc[idx]['question_content'].values[0], 'Distance': val[1]})
    #                     print(idx)
    #                 df = pd.DataFrame(recommend_frame, index=range(1, n_movies_to_reccomend + 1))
    #                 print(df)
    #                 # similar = df.index[df['Title'] == True].tolist()
    #                 # json_record = (df.apply(lambda x: [x.to_dict()], axis=1).reset_index(name='Distance').to_json(
    #                 #     orient='records'))
    #                 # json_values = df.to_json(orient='values')
    #                 # # print("json_values = ", json_values, "\n")
    #                 # data = [json.loads(json_values)]
    #                 # # context=[]
    #                 # # context['data'] = json.loads(json_record)/
    #                 df.sort_values('Distance', ascending=False, inplace=True)
    #                 output = df[1:].head(10)
    #                 json_record = output.reset_index().to_json(orient='records')
    #                 # data = []
    #                 data = json.loads(json_record)
    #                 context = {'q': data}
    #                 print(context)
    #
    #             # else:
    #             #     return render(request, "forum/test2.html")
    #
    #         # get_movie_recommendation(a)
    #         print(a)
    #         return render(request, "forum/test2.html", context)


def ContactUs(request):
    return render(request, "forum/contactus.html")