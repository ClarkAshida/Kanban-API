import re
from django.utils import timezone
from rest_framework import serializers
from django.core.validators import RegexValidator
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import User, Column, Card, Task, Tag, Comment, Notification, Attachment

# Serializer para o modelo User
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'
        read_only_fields = ['id', 'is_staff', 'is_active']

    def validate_login(self, value):
        # Expressão regular para o padrão de login aceitável
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
    # Método para validar o nome da coluna, não pode estar vazia
    def validate_name(self, value):
        if not value.strip():
            raise serializers.ValidationError("O nome da coluna não pode estar vazio.")
        return value
    # Método para validar a posição da coluna, não pode ser um número negativo
    def validate_position(self, value):
        if value < 0:
            raise serializers.ValidationError("A posição não pode ser um número negativo.")
        return value
    # Método para validar a posição da coluna, não pode haver duas colunas com a mesma posição para o mesmo usuário
    def validate(self, data):
        fk_user = data.get('fk_user')
        position = data.get('position')

        if not fk_user:
            raise serializers.ValidationError("O usuário associado deve ser fornecido para a coluna.")
        if Column.objects.filter(position=position, fk_user=fk_user).exists():
            raise serializers.ValidationError({
                'position': 'Você já possui uma coluna nessa posição.'
            })
        
        return data

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

    # Método para validar a prioridade do cartão, deve ser uma das opções permitidas
    def validate_priority(self, value):
        valid_priorities = dict(Card.PRIORITY_CHOICES).keys()  # Obtém as chaves válidas ('U', 'I', 'M', 'B')
        if value not in valid_priorities:
            raise serializers.ValidationError(
                "Prioridade inválida. Escolha uma das seguintes opções: 'U' (Urgente), 'I' (Importante), 'M' (Média), 'B' (Baixa)."
            )
        return value
    
    # Método para validar a posição do cartão, não pode ser um número negativo
    def validate_position(self, value):
        if value is not None and value < 0:
            raise serializers.ValidationError("A posição não pode ser um número negativo.")
        return value
    
    # Método para validar a relação entre data de início e data de prazo final. Valida posição única por coluna
    def validate(self, data):
        fk_user = data.get('fk_user')
        fk_column = data.get('fk_column')
        position = data.get('position')
        start_date = data.get('start_date')
        due_date = data.get('due_date')

        # Verifica que o `fk_user` do Card é o mesmo `fk_user` do Column
        if fk_column and fk_column.fk_user != fk_user:
            raise serializers.ValidationError(
                "O usuário do cartão deve ser o mesmo que o usuário associado à coluna selecionada."
            )
        # Validação de unicidade de `position` por coluna
        if position is not None and fk_column:
            # Exclui o próprio objeto da validação para casos de atualização
            queryset = Card.objects.filter(position=position, fk_column=fk_column)
            if self.instance:
                queryset = queryset.exclude(id=self.instance.id)

            if queryset.exists():
                raise serializers.ValidationError({
                    'position': 'Já existe um cartão nesta posição para esta coluna. Cada posição deve ser única dentro de uma coluna.'
                })

        if start_date and due_date and due_date < start_date:
            raise serializers.ValidationError({
                'due_date': 'A data de vencimento não pode ser anterior à data de início.'
            })
    
        return data


# Serializer para o modelo Task
class TaskSerializer(serializers.ModelSerializer):
    fk_card = CardSerializer(read_only=True)  # Se você quiser incluir os dados completos do cartão
    fk_card_id = serializers.PrimaryKeyRelatedField(queryset=Card.objects.all(), source='fk_card')

    class Meta:
        model = Task
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate(self, data):
        """
        Validações:
        - Garante que `completed_at` seja automaticamente preenchido se `completed=True`.
        - Exige `completed_at` caso `completed=True`.
        - Garante que `position` é única dentro de cada `fk_card`.
        """
        completed = data.get('completed')
        completed_at = data.get('completed_at')
        position = data.get('position')
        fk_card = data.get('fk_card')

        # Atribui automaticamente `completed_at` se `completed=True` e `completed_at` não estiver preenchido
        if completed and not completed_at:
            data['completed_at'] = timezone.now()

        # Valida que `completed_at` está presente se `completed=True`
        elif completed and completed_at is None:
            raise serializers.ValidationError({
                'completed_at': 'A data de conclusão deve ser fornecida quando a tarefa é marcada como concluída.'
            })

        # Verifica a unicidade de `position` para cada `fk_card`
        if position is not None and fk_card:
            # Exclui a instância atual da validação (para evitar conflito em atualizações)
            queryset = Task.objects.filter(position=position, fk_card=fk_card)
            if self.instance:
                queryset = queryset.exclude(id=self.instance.id)

            if queryset.exists():
                raise serializers.ValidationError({
                    'position': 'Já existe uma tarefa nesta posição para este cartão. A posição deve ser única dentro de cada cartão.'
                })

        return data


# Serializer para o modelo Tag
class TagSerializer(serializers.ModelSerializer):
    color = serializers.CharField(
        validators=[RegexValidator(
            regex=r'^#[0-9A-Fa-f]{6}$',
            message="A cor deve estar no formato hexadecimal, como #FFFFFF ou #000000."
        )]
    )

    class Meta:
        model = Tag
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate_name(self, value):
        if Tag.objects.filter(name=value).exists():
            raise serializers.ValidationError("Essa tag já existe.")
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

    # Método para validar a mensagem da notificação, não pode estar vazia
    def validate_message(self, value):
        if not value.strip():
            raise serializers.ValidationError("A mensagem não pode estar vazia.")
        return value
    
    # Método para validar o tipo de notificação está entre as opções permitidas.
    def validate_notification_type(self, value):
        valid_types = dict(Notification.NOTIFICATION_TYPES).keys()  # Obtém as chaves válidas ('comment', 'task_completed', 'card_moved')
        if value not in valid_types:
            raise serializers.ValidationError(
                "Tipo de notificação inválido. Escolha uma das seguintes opções: 'comment' (Comentário), 'task_completed' (Tarefa Concluída), 'card_moved' (Cartão Movido)."
            )
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

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    username_field = 'login'  # Especifica 'login' como o campo de identificação

    def validate(self, attrs):
        # Substitui `username` por `login` como campo de identificação no SimpleJWT
        login = attrs.get("login")
        password = attrs.get("password")

        try:
            self.user = User.objects.get(login=login)
        except User.DoesNotExist:
            raise serializers.ValidationError("Usuário não encontrado.")

        if not self.user.check_password(password):
            raise serializers.ValidationError("Credenciais inválidas.")

        return super().validate(attrs)
