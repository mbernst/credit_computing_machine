import copy
from django.conf import settings

from rest_framework import generics, status
from django.contrib.auth import authenticate

from app.models import CreditGroup, CreditScore,CreditUser
from .serializers import CreditGroupCreateSerializer
from .serializers import CreditUserCreateSerializer ,CreditGroupUpdateSerializer,CreditUserScoreUpdateSerializer
from privateurl.models import PrivateUrl
from rest_framework.response import Response
from . import email_service
from credit_computing_machine.drf_custom_exceptions import CustomAPIException
from django.db import transaction
from django.db import IntegrityError




class CreditGroupCreateApi(generics.CreateAPIView):
    serializer_class = CreditGroupCreateSerializer

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        response = {}
        request_data = copy.deepcopy(request.data)

        credit_users = request_data.get('credit_users')
        credit_admin_users = request_data.get('credit_admin')
        request_data.pop('credit_users')
        request_data.pop('credit_admin')
        credit_group_serializer_data = CreditGroupCreateSerializer(data=request_data)
        if credit_group_serializer_data.is_valid():
            credit_group = credit_group_serializer_data.save()
            for credit_user in credit_users:
                credit_user['credit_group'] = credit_group.id
            for credit_user in credit_admin_users:
                credit_user['credit_group'] = credit_group.id
                credit_user['is_admin'] = True
            credit_user_serializer_data = CreditUserCreateSerializer(data=credit_users, many=True)
            credit_admin_user_serializer_data = CreditUserCreateSerializer(data=credit_admin_users, many=True)
            if credit_admin_user_serializer_data.is_valid():
                if credit_user_serializer_data.is_valid():
                    try:
                        credit_admin_users = credit_admin_user_serializer_data.save()
                        credit_users = credit_user_serializer_data.save()
                    except IntegrityError as e:
                        raise CustomAPIException({'email':'Two user cannot have same email within same group'})

                    user_ids = [i.id for i in credit_users]
                    for index,user_id in  enumerate(user_ids):
                        for internal_index, internal_user_id in enumerate(user_ids):
                            if user_id != internal_user_id:
                                CreditScore.objects.create(from_credit_user_id= user_id,to_credit_user_id =internal_user_id,credit_group= credit_group ,score = 0)

                    email_service.send_invite_email_to_non_admin_credit_group(credit_group.id)

                    response = {'msg': 'Group created'}
                else:
                    raise CustomAPIException(credit_user_serializer_data.errors)
            else:
                raise CustomAPIException(credit_admin_user_serializer_data.errors)
        else:
            raise CustomAPIException(credit_group_serializer_data.errors)

        return Response(response, status=status.HTTP_200_OK)

class CreditGroupRetrieveUpdateAPI(generics.RetrieveUpdateAPIView):
    serializer_class = CreditGroupUpdateSerializer

    def get_object(self):
        try:
            return CreditGroup.objects.get(privateurl__token__exact=self.kwargs['token'])
        except CreditGroup.DoesNotExist:
            return None

class CreditUserScoresRetrieveUpdateAPI(generics.RetrieveUpdateAPIView):
    serializer_class = CreditUserScoreUpdateSerializer

    def get_object(self):
        try:
            return CreditUser.objects.get(privateurl__token__exact=self.kwargs['token'])
        except CreditUser.DoesNotExist:
            return None


