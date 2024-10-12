from datetime import timezone
from rest_framework import serializers
from .models import User, Column, Card, Task, Tag, Comment, Notification, Attachment

# Serializer para o modelo User
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'cpf', 'address', 'birth_date', 'is_staff', 'is_active']
        read_only_fields = ['id', 'is_staff', 'is_active']

    def validate_cpf(self, value):
        if len(value) != 11 or not value.isdigit():
            raise serializers.ValidationError("O CPF deve conter exatamente 11 dígitos numéricos.")
        return value

    def validate_birth_date(self, value):
        if value and value > timezone.now().date():
            raise serializers.ValidationError("A data de nascimento não pode estar no futuro.")
        return value


# Serializer para o modelo Column
class ColumnSerializer(serializers.ModelSerializer):
    class Meta:
        model = Column
        fields = ['id', 'name', 'position', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
    def validate_name(self, value):
        if not value.strip():
            raise serializers.ValidationError("O nome da coluna não pode estar vazio.")
        return value

    def validate_position(self, value):
        if value < 0:
            raise serializers.ValidationError('A posição não pode ser um número negativo.')
        if Column.objects.filter(position=value).exists():
            raise serializers.ValidationError('Já existe uma coluna com essa posição.')
        return value


# Serializer para o modelo Card
class CardSerializer(serializers.ModelSerializer):
    fk_column = ColumnSerializer(read_only=True)  # Se você quiser incluir os dados completos da coluna
    fk_user = UserSerializer(read_only=True)      # Se você quiser incluir os dados completos do usuário
    fk_column_id = serializers.PrimaryKeyRelatedField(queryset=Column.objects.all(), source='fk_column')
    fk_user_id = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), source='fk_user')

    class Meta:
        model = Card
        fields = [
            'id', 'title', 'description', 'fk_column', 'fk_column_id', 'position', 'start_date', 'due_date',
            'priority', 'category', 'fk_user', 'fk_user_id', 'created_at', 'updated_at', 'fk_assigned_user'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def validate_due_date(self, value):
        start_date = self.initial_data.get('start_date')
        if start_date and value and value < start_date:
            raise serializers.ValidationError("A data de vencimento não pode ser anterior à data de início.")
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
        fields = ['id', 'title', 'position', 'fk_card', 'fk_card_id', 'completed', 'completed_at', 'created_at', 'updated_at']
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
        fields = ['id', 'name', 'color', 'created_at', 'updated_at']
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
        fields = ['id', 'comment_text', 'fk_card', 'fk_card_id', 'fk_user', 'fk_user_id', 'created_at']
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
        fields = ['id', 'message', 'notification_type', 'read', 'fk_user', 'fk_user_id', 'created_at']
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
        fields = ['id', 'file', 'fk_card', 'fk_card_id', 'uploaded_by', 'uploaded_by_id', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate_file(self, value):
        if value.size > 1024 * 1024 * 5:  # Limitar o tamanho do arquivo a 5MB (1KB * 1MB * 5 = 5MB)
            raise serializers.ValidationError("O arquivo não pode ter mais de 5MB.")
        if not value.name.endswith(('.jpg', '.png', '.pdf')):
            raise serializers.ValidationError("Formato de arquivo não permitido. Use .jpg, .png ou .pdf.")
        return value
