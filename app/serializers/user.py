from rest_framework import serializers
from app.models.address import Address
from app.models.user import User
from app.models.vehicle import Vehicle
from app.serializers.address import AddressSerializer
from app.serializers.join_reader import JoinReader
from app.serializers.vehicle import VehicleSerializer
from app.serializers.order import OrderSerializer


class UserSerializer(JoinReader):
    password = serializers.CharField(write_only=True, required=True)
    confirm_password = serializers.CharField(write_only=True, required=True)

    address_set = AddressSerializer(many=True, required=False,)
    vehicle_set = VehicleSerializer(many=True, required=False,)
    order_set = OrderSerializer(many=True, required=False, read_only=True)

    class Meta:
        model = User
        fields = (
            'id', 'email', 'username', 'date_created', 'date_modified',
            'firstname', 'lastname', 'password', 'confirm_password', 'is_admin', 'order_set')
        join_fields = {
            'address_set': Address,
            'vehicle_set': Vehicle,
        }
        for key, value in join_fields.items():
            fields += (key,)
        read_only_fields = ('date_created', 'date_modified')

    def to_representation(self, instance):
        ret = super(UserSerializer, self).to_representation(instance)
        fields_to_pop = ['id', 'address_set', 'vehicle_set', 'order_set']
        if 'user' in self.context and instance != self.context['user']:
            [ret.pop(field, '') for field in fields_to_pop]
        return ret

    def create(self, validated_data):
        joins = self.create_joins(validated_data)
        user = User.objects.create_user(**validated_data)
        for value in joins:
            class_name = value.get("class_name")
            data = value.get("data")
            for obj in data:
                class_name.objects.create(user=user, **obj)
        return user

    def update(self, instance, validated_data):
        joins = self.update_joins(instance, validated_data)
        if 'password' in validated_data:
            password = validated_data.pop('password')
            instance.set_password(password)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        for value in joins:
            class_name = value.get("class_name")
            data = value.get("data")
            for obj in data:
                class_name.objects.create(user=instance, **obj)
        return instance

    def validate(self, data):
        """
        Ensure the passwords are the same
        """
        if 'password' in data:
            if data['password'] != data['confirm_password']:
                raise serializers.ValidationError(
                    "The passwords have to be the same"
                )
        return data
