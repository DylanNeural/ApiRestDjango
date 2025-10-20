import json
from datetime import datetime
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponseNotAllowed
from django.views.decorators.csrf import csrf_exempt
from .models import Users
from django.core.exceptions import ObjectDoesNotExist
from .models import Users, DossierSante

DATE_FMT = "%d/%m/%Y"  # JJ/MM/AAAA

def _serialize(u: Users):
    return {
        "id": u.id,  # ton champ id (string) si tu l'as gardé ; sinon la PK auto de Django
        "prenom": u.prenom,
        "age": u.age,
        "dateAnniversaire": u.dateAnniversaire.strftime(DATE_FMT),
    }

def _parse_body(request):
    try:
        return json.loads(request.body.decode("utf-8"))
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
    }

def _get_dossier_or_none(user: Users):
    try:
        return user.dossier_sante
    except ObjectDoesNotExist:
        return None

@csrf_exempt
def dossier_sante(request, pk: int):
    """
    /api/users/<int:pk>/dossier/
      GET    -> retourne le dossier (404 si absent)
      POST   -> crée le dossier si absent (201) ; 409 s'il existe déjà
      PATCH  -> met à jour les champs fournis (404 si absent)
      DELETE -> supprime le dossier (204), idempotent
    """
    # 1) récupérer l'utilisateur
    try:
        user = Users.objects.get(pk=pk)
    except Users.DoesNotExist:
        return JsonResponse({"detail": "User not found"}, status=404)

    # 2) router
    if request.method == "GET":
        ds = _get_dossier_or_none(user)
        if ds is None:
            return JsonResponse({"detail": "Dossier not found"}, status=404)
        return JsonResponse(_serialize_dossier(ds))

    if request.method == "POST":
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