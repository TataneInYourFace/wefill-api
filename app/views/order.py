from datetime import datetime
import re
import pytz
from django.db.models import Q
from rest_framework import status
from rest_framework.response import Response
from app.serializers.order import OrderSerializer
from app.models.order import Order
from app.views.simple_modelview import SimpleModelViewSet


class OrderViewSet(SimpleModelViewSet):

    model_class = Order
    serializer_class = OrderSerializer

    def list(self, request, **kwargs):
        q = Q()
        if "start_date" in request.query_params:
            if not re.match(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", request.query_params.get("start_date")):
                return Response({"errors": "start_date should have YYYY-MM-DD format"},
                                status=status.HTTP_400_BAD_REQUEST)
            start_date = datetime.strptime(request.query_params.get("start_date"), '%Y-%m-%d')
            aware_start = start_date.replace(tzinfo=pytz.UTC)
            q &= Q(date_refill__gte=aware_start)
        if "end_date" in request.query_params:
            if not re.match(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", request.query_params.get("end_date")):
                return Response({"errors": "end_date should have YYYY-MM-DD format"},
                                status=status.HTTP_400_BAD_REQUEST)
            end_date = datetime.strptime(request.query_params.get("end_date"), '%Y-%m-%d')
            end_date_real = end_date.replace(hour=23, minute=59, second=59, microsecond=999999, tzinfo=pytz.UTC)
            q &= Q(date_refill__lte=end_date_real)
        if request.user.is_admin:
            models = self.model_class.objects.filter(q)
        else:
            q &= Q(user=request.user)
            models = self.model_class.objects.filter(q)
        if models is None:
            return Response(status=status.HTTP_204_NO_CONTENT)
        serializer = self.serializer_class(models, many=True)
        return Response(serializer.data)

    def destroy(self, request, id=None, **kwargs):
        return Response({"errors": "Orders can't be deleted."}, status=status.HTTP_401_UNAUTHORIZED)


