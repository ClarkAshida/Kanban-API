import re
from datetime import datetime
from rest_framework import serializers
from .models import User, Column, Card, Task, Tag, Comment, Notification, Attachment

# Serializer para o modelo User
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'
        read_only_fields = ['id', 'is_staff', 'is_active']

    def validate_login(self, value):
        # Expressão regular para o padrão de login do Instagram
        pattern = r"^(?!.*\.\.)(?!.*\.$)(?!^[0-9])(?!^[._])(?!.*[._]{2})[a-zA-Z0-9._]{1,30}$"
        
        if not re.match(pattern, value):
            raise serializers.ValidationError(
                "O login deve ter entre 1 e 30 caracteres, usar apenas letras, números, "
                "pontos ou underscores. Não pode começar com números ou pontos, "
                "nem terminar com ponto ou conter pontos consecutivos."
            )
        return value

    def validate_password(self, value):
        # Expressão regular para garantir uma senha forte
        password_pattern = (
            r'^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$'
        )
        if not re.match(password_pattern, value):
            raise serializers.ValidationError(
                "A senha deve ter pelo menos 8 caracteres, incluindo uma letra maiúscula, "
                "uma letra minúscula, um número e um caractere especial (@, $, !, %, *, ?, &)."
            )
        return value

    def create(self, validated_data):
        # Usando o método create_user do UserManager para garantir que a senha seja tratada corretamente
        user = User.objects.create_user(
            login=validated_data['login'],
            name=validated_data['name'],
            password=validated_data.get('password')
        )
        return user

    def update(self, instance, validated_data):
        # Se a senha estiver presente nos dados validados, chamamos o método set_password
        password = validated_data.get('password', None)
        if password:
            instance.set_password(password)
        instance.name = validated_data.get('name', instance.name)
        instance.login = validated_data.get('login', instance.login)
        instance.save()
        return instance

# Serializer para o modelo Column
class ColumnSerializer(serializers.ModelSerializer):
    class Meta:
        model = Column
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']
    def validate_name(self, value):
        if not value.strip():
            raise serializers.ValidationError("O nome da coluna não pode estar vazio.")
        return value
    #PRECISO VALIDAR MELHOR A POSIÇÃO PARA VER SE O USUÁRIO JÁ POSSUI UMA COLUNA COM A MESMA POSIÇÃO
    def validate_position(self, value):
        # Recupera o usuário autenticado para verificar se ele já tem uma coluna com a mesma posição
        user = self.context['request'].user
        if value < 0:
            raise serializers.ValidationError('A posição não pode ser um número negativo.')
        if Column.objects.filter(position=value, fk_user=user).exists():
            raise serializers.ValidationError('Você já possui uma coluna com essa posição.')
        return value

# Serializer para o modelo Card
class CardSerializer(serializers.ModelSerializer):
    fk_column = ColumnSerializer(read_only=True)
    fk_user = UserSerializer(read_only=True)
    fk_column_id = serializers.PrimaryKeyRelatedField(queryset=Column.objects.all(), source='fk_column')
    fk_user_id = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), source='fk_user')

    class Meta:
        model = Card
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def validate_due_date(self, value):
        if value and value.date() < datetime.now().date():
            raise serializers.ValidationError("A data de vencimento não pode ser no passado.")
        return value

    def validate_position(self, value):
        if value < 0:
            raise serializers.ValidationError('A posição não pode ser um número negativo.')
        if Card.objects.filter(position=value, fk_column=self.initial_data.get('fk_column')).exists():
            raise serializers.ValidationError('Já existe um cartão com essa posição.')
        return value


# Serializer para o modelo Task
class TaskSerializer(serializers.ModelSerializer):
    fk_card = CardSerializer(read_only=True)  # Se você quiser incluir os dados completos do cartão
    fk_card_id = serializers.PrimaryKeyRelatedField(queryset=Card.objects.all(), source='fk_card')

    class Meta:
        model = Task
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate_position(self, value):
        if value < 0:
            raise serializers.ValidationError("A posição não pode ser um número negativo.")
        if Task.objects.filter(position=value, fk_card=self.initial_data.get('fk_card')).exists():
            raise serializers.ValidationError("Já existe uma tarefa com essa posição.")
        return value

    def validate_finalization(self, data):
        if data.get('completed') and not data.get('completed_at'):
            raise serializers.ValidationError("A data de conclusão deve ser fornecida quando a tarefa é marcada como concluída.")
        return data


# Serializer para o modelo Tag
class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate_name(self, value):
        if Tag.objects.filter(name=value).exists():
            raise serializers.ValidationError("Essa tag já existe.")
        return value
    def validate_color(self, value):
        if not value.startswith('#'):
            raise serializers.ValidationError("A cor deve ser uma string hexadecimal.")
        if len(value) != 7:
            raise serializers.ValidationError("A cor deve ter 7 caracteres.")
        return value


# Serializer para o modelo Comment
class CommentSerializer(serializers.ModelSerializer):
    fk_card = CardSerializer(read_only=True)
    fk_user = UserSerializer(read_only=True)
    fk_card_id = serializers.PrimaryKeyRelatedField(queryset=Card.objects.all(), source='fk_card')
    fk_user_id = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), source='fk_user')

    class Meta:
        model = Comment
        fields = '__all__'
        read_only_fields = ['id', 'created_at']

    def validate_comment_text(self, value):
        if not value.strip():
            raise serializers.ValidationError("O comentário não pode estar vazio.")
        return value

# Serializer para o modelo Notification
class NotificationSerializer(serializers.ModelSerializer):
    fk_user = UserSerializer(read_only=True)
    fk_user_id = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), source='fk_user')

    class Meta:
        model = Notification
        fields = '__all__'
        read_only_fields = ['id', 'created_at']

    def validate_message(self, value):
        if not value.strip():
            raise serializers.ValidationError("A mensagem não pode estar vazia.")
        return value


# Serializer para o modelo Attachment
class AttachmentSerializer(serializers.ModelSerializer):
    fk_card = CardSerializer(read_only=True)
    uploaded_by = UserSerializer(read_only=True)
    fk_card_id = serializers.PrimaryKeyRelatedField(queryset=Card.objects.all(), source='fk_card')
    uploaded_by_id = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), source='uploaded_by')

    class Meta:
        model = Attachment
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate_file(self, value):
        if value.size > 1024 * 1024 * 5:  # Limitar o tamanho do arquivo a 5MB (1KB * 1MB * 5 = 5MB)
            raise serializers.ValidationError("O arquivo não pode ter mais de 5MB.")
        if not value.name.endswith(('.jpg', '.png', '.pdf')):
            raise serializers.ValidationError("Formato de arquivo não permitido. Use .jpg, .png ou .pdf.")
        return value
