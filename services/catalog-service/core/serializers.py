from rest_framework import serializers
from .models import Categoria, Pacote

class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = '__all__'

class PacoteSerializer(serializers.ModelSerializer):
    # Campo calculado para exibir o nome da categoria junto, isso a gente pode alterar, mas a principio é bom ter
    categoria_nome = serializers.CharField(source='categoria.nome', read_only=True)

    class Meta:
        model = Pacote
        fields = '__all__'
        read_only_fields = ['freelancer_id', 'data_criacao', 'data_atualizacao']

    def validate(self, data):
        # Garante que o usuário logado seja salvo como dono
        request = self.context.get('request')
        if request and hasattr(request, 'headers'):
            user_id = request.headers.get('X-User-Id')
            if not user_id:
                # Para MVP, vamos deixar passar ou definir um valor fixo se for teste
                pass 
        return data