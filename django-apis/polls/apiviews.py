from rest_framework import generics
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework import viewsets


from .models import Poll, Choice
from .serializers import (
    PollSerializer,
    ChoiceSerializer,
    VoteSerializer,
    UserSerializer,
)
from django.contrib.auth import authenticate
from rest_framework.exceptions import PermissionDenied


class PollViewSet(
    viewsets.ModelViewSet
):  # allows all or most of CRUD operations on a model
    queryset = Poll.objects.all()
    serializer_class = PollSerializer

    def destroy(self, request, *args, **kwargs):
        poll = Poll.objects.get(pk=self.kwargs["pk"])
        if not poll.created_by == self.request.user:
            raise PermissionDenied("You can not delete this poll")
        return super().destroy(request, *args, **kwargs)


class PollList(
    generics.ListCreateAPIView
):  # generics.* allows some operations on a model
    queryset = Poll.objects.all()
    serializer_class = PollSerializer


class PollDetail(generics.RetrieveDestroyAPIView):
    queryset = Poll.objects.all()
    serializer_class = PollSerializer


class ChoiceList(generics.ListCreateAPIView):
    def get_queryset(self):
        queryset = Choice.objects.filter(poll_id=self.kwargs["pk"])
        return queryset

    def post(self, request, *args, **kwargs):
        poll = Poll.objects.get(pk=self.kwargs["pk"])
        if not poll.created_by == self.request.user:
            raise PermissionDenied("You can not create choice for this poll")
        return super().post(request, *args, **kwargs)

    serializer_class = ChoiceSerializer


class CreateVote(APIView):  # for customizing the behaviour.
    def post(self, request, pk, choice_pk):
        voted_by = request.data.get("voted_by")
        data = {"choice": choice_pk, "poll": pk, "voted_by": voted_by}
        serializer = VoteSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserCreate(generics.CreateAPIView):
    authentication_classes = ()
    permission_classes = ()
    serializer_class = UserSerializer


class LoginView(APIView):
    permission_classes = ()

    def post(
        self,
        request,
    ):
        username = request.data.get("username")
        password = request.data.get("password")
        user = authenticate(username=username, password=password)
        if user:
            return Response({"token": user.auth_token.key})
        else:
            return Response(
                {"error": "Wrong Credentials"}, status=status.HTTP_400_BAD_REQUEST
            )
