import json
from datetime import datetime
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponseNotAllowed
from django.views.decorators.csrf import csrf_exempt
from .models import Users
from django.core.exceptions import ObjectDoesNotExist
from .models import Users, DossierSante
from django.contrib.auth.models import User
from functools import wraps
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.db import transaction
import requests

DATE_FMT = "%d/%m/%Y"  # JJ/MM/AAAA
User = get_user_model()

def _serialize(userJson: Users):
    return {
        "id": userJson.id,
        "prenom": userJson.prenom,
        "age": userJson.age,
        "dateAnniversaire": userJson.dateAnniversaire.strftime(DATE_FMT),
    }

def _parse_body(req):
    try:
        return json.loads(req.body.decode("utf-8"))
    except Exception:
        raise ValueError("JSON invalide")

def _parse_date_or_400(s: str):
    try:
        return datetime.strptime(s, DATE_FMT).date()
    except Exception:
        raise ValueError("dateAnniversaire doit être au format JJ/MM/AAAA")

def _parse_int_or_400(v, name):
    try:
        return int(v)
    except Exception:
        raise ValueError(f"{name} doit être un entier")
    
def _is_self(request, target_user: Users) -> bool:
    
    """
    Autorise si l'appelant est connecté ET propriétaire du profil.
    """
    if not request.user.is_authenticated:
        return False
    # si Users.account n'est pas encore renseigné, refuse par défaut
    return (target_user.account_id == request.user.id)


def _is_self_or_admin(request, target_user: Users) -> bool:
    
    """
    Autorise si l'appelant est connecté ET (admin) OU (propriétaire du profil).
    """
    if not request.user.is_authenticated:
        return False
    if request.user.is_staff:
        return True
    # si Users.account n'est pas encore renseigné, refuse par défaut
    return (target_user.account_id == request.user.id)

def _is_admin(request, target_user: Users) -> bool:
    
    """
    Autorise si l'appelant est connecté ET (admin).
    """
    if not request.user.is_authenticated:
        return False
    if request.user.is_admin:
        return True

def _auth_required_json(view):
    # version JSON de login_required (évite la redirection HTML)
    from functools import wraps
    @wraps(view)
    def w(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({"detail": "Authentication required"}, status=401)
        return view(request, *args, **kwargs)
    return w

@csrf_exempt
def users_collection(request):

    if request.method == "GET":
        data = [_serialize(u) for u in Users.objects.all()]
        return JsonResponse(data, safe=False)

    if request.method == "POST":
        try:
            body = _parse_body(request)


            id_val = body.get("id", None)

            u = Users(
                prenom = body.get("prenom", ""),
                age = _parse_int_or_400(body.get("age"), "age"),
                dateAnniversaire = _parse_date_or_400(body.get("dateAnniversaire")),
            )

            if hasattr(Users, "id") and id_val is not None:
                u.id = id_val

            u.save()
            return JsonResponse(_serialize(u), status=201)

        except ValueError as e:
            return HttpResponseBadRequest(str(e))

    return HttpResponseNotAllowed(["POST"])


@csrf_exempt
def users_detail(request, pk: str):
    
    try:
        try:
            u = Users.objects.get(pk=pk)
        except (Users.DoesNotExist, ValueError):
            u = Users.objects.get(id=pk)
    except Users.DoesNotExist:
        return JsonResponse({"detail": "Not found"}, status=404)

    if request.method == "GET":
        return JsonResponse(_serialize(u))

    if request.method == "PATCH":
        try:
            body = _parse_body(request)
            if "prenom" in body:
                u.prenom = body.get("prenom") or ""
            if "age" in body:
                u.age = _parse_int_or_400(body.get("age"), "age")
            if "dateAnniversaire" in body:
                u.dateAnniversaire = _parse_date_or_400(body.get("dateAnniversaire"))
            if "id" in body and hasattr(Users, "id"):
                new_id = body.get("id")
                if not new_id:
                    return HttpResponseBadRequest("Le champ 'id' ne peut pas être vide.")
                if new_id != str(u.id) and Users.objects.filter(id=new_id).exists():
                    return HttpResponseBadRequest("Un utilisateur avec ce nouvel id existe déjà.")
                u.id = new_id

            u.save()
            return JsonResponse(_serialize(u))
        except ValueError as e:
            return HttpResponseBadRequest(str(e))

    if request.method == "DELETE":
        u.delete()
        return JsonResponse({}, status=204)

    return HttpResponseNotAllowed(["GET", "PATCH", "DELETE"])




# /////////////////////////////////////////////////////////////




def _serialize_dossier(ds: DossierSante) -> dict:
    return {
        "user_id": ds.user.pk,
        "groupe_sanguin": ds.groupe_sanguin or "",
        "allergies": ds.allergies or "",
        "medecin_traitant": ds.medecin_traitant or "",
        "department_medical": ds.department_medical or "",
    }


def _get_dossier_or_none(user: Users):
    try:
        return user.dossier_sante
    except ObjectDoesNotExist:
        return None
    
    
@_auth_required_json
@csrf_exempt
def dossier_sante(request, pk: int):

    
    # 1) récupérer l'utilisateur
    try:
        user = Users.objects.get(pk=pk)
    except Users.DoesNotExist:
        return JsonResponse({"detail": "User not found"}, status=404)


    if not _is_self_or_admin(request, user):
        return JsonResponse({"detail": "Forbidden"}, status=403)
    
    
    # 2) router
    if request.method == "GET":
        ds = _get_dossier_or_none(user)
        if ds is None:
            return JsonResponse({"detail": "Dossier not found"}, status=404)
        return JsonResponse(_serialize_dossier(ds))

    if request.method == "POST":
        try:
            body = _parse_body(request)


            id_val = body.get("id", None)

            u = Users(
                prenom = body.get("prenom", ""),
                age = _parse_int_or_400(body.get("age"), "age"),
                dateAnniversaire = _parse_date_or_400(body.get("dateAnniversaire")),
            )

            if hasattr(Users, "id") and id_val is not None:
                u.id = id_val

            u.save()

        except ValueError as e:
            return HttpResponseBadRequest(str(e))
        
        ds = _get_dossier_or_none(user)
        if ds is not None:
            return JsonResponse({"detail": "Dossier already exists"}, status=409)

        try:
            body = json.loads(request.body.decode("utf-8")) if request.body else {}
        except Exception:
            return HttpResponseBadRequest("JSON invalide")

        ds = DossierSante.objects.create(
            user=user,
            groupe_sanguin=(body.get("groupe_sanguin") or "").upper(),
            allergies=body.get("allergies") or "",
            medecin_traitant=body.get("medecin_traitant") or "",
        )
        return JsonResponse(_serialize_dossier(ds), status=201)

    if request.method == "PATCH":
        ds = _get_dossier_or_none(user)
        if ds is None:
            return JsonResponse({"detail": "Dossier not found"}, status=404)

        try:
            body = json.loads(request.body.decode("utf-8"))
        except Exception:
            return HttpResponseBadRequest("JSON invalide")

        if "groupe_sanguin" in body:
            ds.groupe_sanguin = (body.get("groupe_sanguin") or "").upper()
        if "allergies" in body:
            ds.allergies = body.get("allergies") or ""
        if "medecin_traitant" in body:
            ds.medecin_traitant = body.get("medecin_traitant") or ""
            
        ds.save()
        return JsonResponse(_serialize_dossier(ds))

    if request.method == "DELETE":
        ds = _get_dossier_or_none(user)
        if ds is not None:
            ds.delete()
        return JsonResponse({}, status=204)

    return HttpResponseNotAllowed(["GET", "POST", "PATCH", "DELETE"])



def login_required_json(view):
    @wraps(view)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({"detail": "Authentication required"}, status=401)
        return view(request, *args, **kwargs)
    return wrapper

@csrf_exempt
def signup_json(request):
    if request.method != "POST":
        return JsonResponse({"detail": "Method not allowed"}, status=405)

    try:
        body = json.loads(request.body.decode("utf-8"))
    except Exception:
        return HttpResponseBadRequest("JSON invalide")

    # champs auth
    username = (body.get("username") or "").strip()
    password = body.get("password") or ""
    email    = (body.get("email") or "").strip()

    if not username or not password:
        return HttpResponseBadRequest("username et password sont requis")
    if User.objects.filter(username=username).exists():
        return JsonResponse({"detail": "username déjà pris"}, status=400)

    # champs profil Users
    try:
        prenom  = (body.get("prenom") or "").strip()
        age     = int(body["age"])
        dateAnniversaire = _parse_date_or_400(body["dateAnniversaire"])   # JJ/MM/AAAA
    except KeyError as e:
        return HttpResponseBadRequest(f"Champ manquant: {e}")
    except ValueError:
        return HttpResponseBadRequest("age doit être un entier et dateAnniversaire au format JJ/MM/AAAA")

    # tout ou rien
    with transaction.atomic():
        auth_user = User.objects.create_user(username=username, email=email, password=password)

        profile = Users.objects.create(
            account=auth_user,          # OneToOne vers l'utilisateur d'auth
            prenom=prenom,
            age=age,
            dateAnniversaire=dateAnniversaire,  # adapte au nom exact de ton champ
        )
        
        r = requests.get(
            "https://smt.esante.gouv.fr/api/terminologies/search",
            params={"searchedText": "BDPM", "pagination": 1, "size": 10},
            timeout=10
        )
        
        r.raise_for_status()
        data = r.json()
        first_theme = (data.get("terminologies") or [{}])[0].get("theme")

        DossierSante.objects.create(user=profile, department_medical = first_theme)  # crée un dossier santé vide

    return JsonResponse({
        "auth": {"id": auth_user.pk, "username": auth_user.username, "email": auth_user.email},
        "profile": {
            "id": profile.pk,
            "prenom": profile.prenom,
            "age": profile.age,
            "dateAnniversaire": profile.dateAnniversaire.strftime(DATE_FMT),
        }
    }, status=201)
    

@csrf_exempt
def login_json(request):
    if request.method != "POST":
        return JsonResponse({"detail": "Method not allowed"}, status=405)
    try:
        body = json.loads(request.body.decode("utf-8"))
    except Exception:
        return HttpResponseBadRequest("JSON invalide")

    username = body.get("username")
    password = body.get("password")
    user = authenticate(request, username=username, password=password)
    if not user:
        return JsonResponse({"detail": "Invalid credentials"}, status=401)

    login(request, user)  # crée une session + envoie un cookie
    return JsonResponse({"detail": "ok", "user": {"id": user.pk, "username": user.username}})

@csrf_exempt
def logout_json(request):
    if request.method != "POST":
        return JsonResponse({"detail": "Method not allowed"}, status=405)
    logout(request)
    return JsonResponse({"detail": "ok"})

@login_required_json
def me_json(request):
    u = request.user
    return JsonResponse({"id": u.pk,
                         "username": u.username,
                         "email": u.email,
                         "prenom": u.profile_user.prenom if hasattr(u, "profile_user") else None,
                         "age": u.profile_user.age if hasattr(u, "profile_user") else None,
                         "dateAnniversaire": u.profile_user.dateAnniversaire.strftime(DATE_FMT) if hasattr(u, "profile_user") else None,
                         })


_is_self
@csrf_exempt
def change_password_json(request):
    if request.method != "PATCH":
        return JsonResponse({"detail": "Method not allowed"}, status=405)
    if not request.user.is_authenticated:
        return JsonResponse({"detail": "Authentication required"}, status=401)
    try:
        body = json.loads(request.body.decode("utf-8"))
    except Exception:
        return HttpResponseBadRequest("JSON invalide")

    old_password = body.get("old_password")
    new_password = body.get("new_password")
    if not old_password or not new_password:
        return HttpResponseBadRequest("old_password et new_password sont requis")

    user = request.user
    if not user.check_password(old_password):
        return JsonResponse({"detail": "Old password is incorrect"}, status=400)

    user.set_password(new_password)
    user.save()
    return JsonResponse({"detail": "Password changed successfully"})

# authentification 
# route qu'un user peut et l'autre non 