import io
from PIL import Image
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseBadRequest

def converter_view(request):
    if request.method == 'GET':
        return render(request, 'tools/image_converter.html')

    if request.method == 'POST':
        arquivo = request.FILES.get('imagem')
        formato_destino = request.POST.get('formato', 'WEBP').upper()

        if not arquivo:
            return HttpResponseBadRequest("Nenhum arquivo enviado.")

        formatos_validos = {
            'JPEG': ('image/jpeg', 'jpg'),
            'PNG': ('image/png', 'png'),
            'WEBP': ('image/webp', 'webp')
        }

        if formato_destino not in formatos_validos:
            return HttpResponseBadRequest("Formato de destino não suportado.")

        try:
            # 1. Abre a imagem em RAM
            img = Image.open(arquivo)

            # 2. Tratamento para JPG (remove transparência se houver)
            if formato_destino == 'JPEG':
                if img.mode in ('RGBA', 'LA', 'P'):
                    fundo = Image.new('RGB', img.size, (255, 255, 255))
                    fundo.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                    img = fundo
                elif img.mode != 'RGB':
                    img = img.convert('RGB')
            elif formato_destino == 'PNG':
                if img.mode not in ('RGB', 'RGBA'):
                    img = img.convert('RGBA')

            # 3. Buffer em memória RAM
            buffer_saida = io.BytesIO()
            img.save(buffer_saida, format=formato_destino, quality=85, optimize=True)
            buffer_saida.seek(0)

            # 4. Prepara o nome de download
            nome_original = arquivo.name.rsplit('.', 1)[0]
            extensao = formatos_validos[formato_destino][1]
            mime_type = formatos_validos[formato_destino][0]
            nome_download = f"{nome_original}_convertido.{extensao}"

            # 5. Resposta enviada direto ao usuário
            response = HttpResponse(buffer_saida.getvalue(), content_type=mime_type)
            response['Content-Disposition'] = f'attachment; filename="{nome_download}"'
            return response

        except Exception as e:
            return HttpResponseBadRequest(f"Falha ao processar arquivo: {str(e)}")