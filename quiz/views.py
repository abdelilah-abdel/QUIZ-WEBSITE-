from django import forms  # For the authentification form
from django.shortcuts import redirect, render  # For rendering (displaying) our content
from .models import Quiz , category , questions, reponse , result  # To acquire the data from our models, then render it
from django.contrib.auth.models import User  # For verifying the user's given login info
from django.db.models import Q  # For searching based on multiple critereas
from django.contrib import messages  # For error flash messages 
from django.contrib.auth import authenticate , login , logout  # For user autentification (login/logout)
from django.contrib.auth.decorators import login_required # Forcing the user to login before doing something we specify
from django.contrib.auth.forms import UserCreationForm
from django.http import JsonResponse
from django.shortcuts import HttpResponse


#landing page
def lading(request):

    
    return render(request, "quiz/landing.html" )



# home page
def index(request):
    quizs = Quiz.objects.all()
    
    categorie = category.objects.all()

    return render(request , "quiz/index.html", {'quiz': quizs, 'category':categorie , 'range':range( 0,5 )})



# Login page
def loginPage(request):
    categorie = category.objects.all()

    page = 'login'
    # Collecting login informations given by the user
    if request.method == 'POST':
        username = request.POST.get('username').lower()
        password = request.POST.get('password')
    
    #if the user does not exist: 
        try:
            user = User.objects.get(username=username) 
        except:
            messages.error(request,'User does not exist')  

    #if the user exists:
        user = authenticate(request , username=username , password=password) #We verify his login infos 
    
    #if the infos are correct we log the user in and create a session:
        if user is not None:
            login(request , user)
            return redirect('index')

        else:
            messages.error(request,'Incorrect username or password')  
    context = {'page':page , 'category':categorie}
    return render(request,"quiz/login_register.html",context)

#user logout
def logoutUser(request):
    logout(request)
    return redirect('index')


# Registration page
def registerPage(request):
    categorie = category.objects.all()

    form = UserCreationForm() #using the django generated registration form
    if request.method =='POST': #we collect the user's given data
       
        form = UserCreationForm(request.POST) #we pass it to the creation form
        
        if form.is_valid(): #we verify if the form is valid
            user = form.save(commit=False) 
            user.username = user.username.lower() #we lower the user's username
            user.save() #we save the user
            login(request,user) #we log the user in
            return redirect('index') #we redirect the user to the home page
             
        else:
            messages.error(request, 'An error occurred during your registration. Please try again.')        
    return render(request,'quiz/login_register.html',{'form':form , 'category':categorie})


def userProfile(request,pk):
    categorie = category.objects.all()

    user = User.objects.get(id=pk)
    context = {'user':user , 'category':categorie}
    return render(request,"quiz/profile.html",context)



#search results page
def search(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''

    quizs = Quiz.objects.filter(
        Q(category__name__icontains=q) |    
        Q(name__icontains=q)
        )
    
    categorie = category.objects.all()

    return render(request , "quiz/search.html", {'quiz': quizs, 'category':categorie , 'q':q})



# Page with all categories
def categories(request):
    categorie = category.objects.all()
    return render(request , "quiz/categories.html",{'category':categorie})

# Page with each category and its quizzes
def category_(request,pk):
    categorie = category.objects.get(id=pk)
    quizs = Quiz.objects.all()
    return render(request, "quiz/category.html", {'category':categorie , 'quiz':quizs})


# page with all quizzes
def allquizzes(request):
    quizs = Quiz.objects.all()   
    return render(request, "quiz/allquizzes.html", {'quiz':quizs}) 


# page with each quiz
def quiz(request,pk):

    quizs = Quiz.objects.get(id=pk)
    context = {'quiz':quizs }
    return render(request , "quiz/quiz.html" , context)


#Acquiring the quiz data (questios/answers) to display it on the page
def quiz_data(request,pk):
    quiz = Quiz.objects.get(id=pk)
    questions = []
    for q in quiz.get_questions():
        answers=[]
        for a in q.get_reponse():
            answers.append(a.description)
        questions.append( {str(q):answers} ) 
    
    return JsonResponse(
        {
            'data':questions,
            'time':quiz.duration,
        }
    ) 





#------- Solution to is_ajax() being undefined in the latest versions of django-----

def is_ajax(request):
    return request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'

def ajax_test(request):
    if is_ajax(request= request):
        message = "This is ajax"
    else:
        message = "Not ajax"
    return HttpResponse(message)
#-----------------------------------------------------------------------
def save_quiz(request, pk):
    # print(request.POST)
    if is_ajax(request=request):
        questions_ = []
        data = request.POST
        data_ = dict(data.lists())
        
        data_.pop('csrfmiddlewaretoken')
        
       

        for k in data_.keys():
            print('key: ',k)
            question= questions.objects.get(description=k)
            questions_.append(question)
        print(questions_)

       

        user = request.user
        quiz=Quiz.objects.get(id = pk)
        
        score = 0
        results = []
        correct_answer = None
        Q_counter=0

        for q in questions_:
            selected_Answer = request.POST.get(q.description)

            if selected_Answer != "":
                question_answers= reponse.objects.filter(questions=q)
                for a in question_answers:
                    if selected_Answer == a.description:
                        if a.correct:
                            score +=1
                            correct_answer = a.description

                    else:
                        if a.correct:
                            correct_answer = a.description

                results.append({ str(q):{'correct_answer': correct_answer,'answered': selected_Answer }})
            
            else:
                results.append({str(q): 'not answered'})
        
        if request.user.is_authenticated:
            result.objects.create(quiz=quiz , user=user, score=score)

        return JsonResponse({ 'score': score, 'results': results })

  




