from django.http import HttpResponse
from django.template import loader
from django.shortcuts import render
from django.utils import timezone


from django.shortcuts import get_object_or_404, render
from django.http import Http404, HttpResponse,HttpResponseRedirect
from django.template import loader
from django.urls import reverse
from .models import Questao, Opcao , Aluno
from django.contrib.auth import authenticate, login

from django.contrib.auth.models import User
from django.contrib.auth import logout



from django.shortcuts import render
from django.conf import settings
from django.core.files.storage import FileSystemStorage

from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import permission_required


from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType


def index(request):
    latest_question_list =Questao.objects.order_by('-pub_data')[:5]
    context = {'latest_question_list':latest_question_list}
    return render(request, 'votacao/index.html', context)

def paginaInsucesso(request):
    latest_question_list = Questao.objects.order_by('-pub_data')[:5]
    context = {'latest_question_list': latest_question_list}
    return render(request, 'votacao/paginaInsucesso.html', context)

def paginaSucesso(request):
    latest_question_list = Questao.objects.order_by('-pub_data')[:5]
    context = {'latest_question_list': latest_question_list}
    return render(request, 'votacao/paginaSucesso.html', context)

@login_required(login_url='/votacao/paginaInsucesso')
def paginaAdmin(request):
    latest_question_list = Questao.objects.order_by('-pub_data')[:5]
    context = {'latest_question_list': latest_question_list}
    return render(request, 'votacao/paginaAdmin.html', context)

def detalhe(request, questao_id):
    #objeto se não dá erro 404
    questao = get_object_or_404(Questao, pk=questao_id)
    return render(request, 'votacao/detalhe.html',
                  {'questao': questao})

def resultados(request, questao_id):
 questao = get_object_or_404(Questao, pk=questao_id)
 return render(request,
'votacao/resultados.html',
{'questao': questao})



def criarQuestao(request):
    if request.method == 'POST':
    # se a invocação veio do form, isto é, está no 2º passo
        try:
            questao_texto =request.POST.get("questao_proposta")
        except KeyError:
            return render(request,'votacao/criarquestao.html')
        if questao_texto:
            # se a questao_texto está preenchida,
            # então vai instanciar a Questão e depois volta ao detalhe
            questao = Questao(questao_texto = questao_texto,pub_data=timezone.now())
            questao.save()
            return HttpResponseRedirect(reverse('votacao:paginaAdmin'))
        else:
            # se a questao_texto não está preenchida, volta ao form
            return HttpResponseRedirect(reverse('votacao:paginaAdmin'))
    else:
        # se a invocação não veio do form, isto é, o 1º passo
        return render(request,'votacao/criarquestao.html')



def nova_opcao(request, questao_id):
    if request.method == 'POST':
    # se a invocação veio do form, isto é, está no 2º passo
        try:
            questao = get_object_or_404(Questao, pk=questao_id)
            opcao_texto = request.POST.get("opcao_proposta")
        except KeyError:
            return render(request, 'votacao/novaopcao.html', {'questao': questao})
        if opcao_texto:
            # se a questao_texto está preenchida,
            # então vai instanciar a Questão e depois volta ao detalhe
            op = Opcao(questao=questao, opcao_texto=opcao_texto , votos=0)
            op.save()
            return HttpResponseRedirect(reverse('votacao:detalhe', args=(questao.id,)))
        else:
            # se a questao_texto não está preenchida, volta ao form
            return render(request, 'votacao/novaopcao.html', {'questao': questao})
    else:
        # se a invocação não veio do form, isto é, o 1º passo
        return render(request,'votacao/novaopcao.html')





def loginview(request):
 username = request.POST['fname']
 password = request.POST['pwd']
 user = authenticate(username=username,
 password=password)
 if user is not None:
    login(request, user)
    if user.is_staff==1:
        return HttpResponseRedirect(reverse('votacao:paginaAdmin'))
    print("sucesso")
    return HttpResponseRedirect(reverse('votacao:paginaSucesso'))

 else:
     print("insucesso")
     paginaInsucesso(request)
     return HttpResponseRedirect(reverse('votacao:paginaInsucesso'))

@login_required(login_url='/votacao/paginaInsucesso')
def apagaQuestao(request, questao_id):
    questao = get_object_or_404(Questao, pk=questao_id)
    questao.delete()
    return HttpResponseRedirect(reverse('votacao:paginaAdmin'))


@login_required(login_url='/votacao/paginaInsucesso')
def apagaOpcao(request,questao_id ):
    questao = get_object_or_404(Questao, pk=questao_id)
    idopcao = request.POST['opcao']
    opcao = get_object_or_404(Opcao, pk=idopcao)
    opcao.delete()
    print("estou aqui")
    return HttpResponseRedirect(reverse('votacao:paginaAdmin'))


def criarUserPage(request):
    return render(request, 'votacao/criarUser.html')

def criarUserButton(request):
    username = request.POST['username']
    email = request.POST['email']
    password = request.POST['password']
    curso = request.POST['curso']

    omeuuser = User.objects.create_user(username,email,password)
    ut = Aluno(user=omeuuser, curso=curso)
    omeuuser.save()
    ut.save()
    user = authenticate(username=username, password=password)
    login(request, user)


    return HttpResponseRedirect(reverse('votacao:index'))

def logoutview(request):
 logout(request)
 return HttpResponseRedirect(reverse('votacao:index'))


def nova_opcaoid(request, questao_id):
    questao = get_object_or_404(Questao, pk=questao_id)
    #questao.opcao_set.create(opcao_texto=request.POST['opcao_proposta'], votos=0)
    op = Opcao(questao=questao, opcao_texto=request.POST['opcao_proposta'], votos=0)
    op.save()
    return HttpResponseRedirect(reverse('votacao:detalhe', args=(questao.id,)))


def voto(request, questao_id):
    questao = get_object_or_404(Questao, pk=questao_id)
    try:
        opcao_seleccionada =questao.opcao_set.get(pk=request.POST['opcao'])
    except (KeyError, Opcao.DoesNotExist):
        # Apresenta de novo o form para votar
        return render(request, 'votacao/detalhe.html', {
 'questao': questao,
'error_message': "Não escolheu uma opção",})
    else:
        opcao_seleccionada.votos += 1
        opcao_seleccionada.save()
    return HttpResponseRedirect(
        reverse('votacao:resultados',
            args=(questao.id,)))


@login_required(login_url='/votacao/paginaInsucesso')
def informacaoPessoal(request):
    filepath = request.FILES.get('myfile', False)
    if request.method == 'POST' and filepath:
        myfile = request.FILES['myfile']
        fs = FileSystemStorage()
        filename = fs.save(myfile.name, myfile)
        uploaded_file_url = fs.url(filename)
        return render(request, 'votacao/informacaoPessoal.html', {'uploaded_file_url': uploaded_file_url})
    return render(request,'votacao/informacaoPessoal.html')

