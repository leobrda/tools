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


def comprimir_view(request):
    if request.method == 'GET':
        return render(request, 'tools/image_compressor.html')

    if request.method == 'POST':
        arquivo = request.FILES.get('imagem')
        # Nível de compressão: padrão 60% de qualidade
        qualidade = int(request.POST.get('qualidade', 60))

        # Trava para garantir valor válido entre 10 e 95
        qualidade = max(10, min(95, qualidade))

        if not arquivo:
            return HttpResponseBadRequest("Nenhum arquivo enviado.")

        try:
            img = Image.open(arquivo)
            formato_original = img.format if img.format else 'JPEG'

            # Se for formato não suportado diretamente para compressão com lossy, padroniza JPEG
            if formato_original not in ('JPEG', 'PNG', 'WEBP'):
                formato_original = 'JPEG'

            buffer_saida = io.BytesIO()

            # Lógica de compressão por formato mantendo o tipo original
            if formato_original == 'JPEG':
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                img.save(buffer_saida, format='JPEG', quality=qualidade, optimize=True)
                mime_type = 'image/jpeg'
                extensao = 'jpg'

            elif formato_original == 'WEBP':
                img.save(buffer_saida, format='WEBP', quality=qualidade, method=6)
                mime_type = 'image/webp'
                extensao = 'webp'

            elif formato_original == 'PNG':
                # PNG é lossless; reduzimos convertendo para paleta de cores adaptativa (P) se solicitado, ou otimizamos
                if img.mode != 'RGBA':
                    img = img.convert('RGB')
                # Quantização para reduzir drasticamente o peso mantendo PNG
                if qualidade < 70:
                    img_otimizada = img.quantize(colors=128, method=2)
                    img_otimizada.save(buffer_saida, format='PNG', optimize=True)
                else:
                    img.save(buffer_saida, format='PNG', optimize=True)
                mime_type = 'image/png'
                extensao = 'png'

            buffer_saida.seek(0)
            nome_original = arquivo.name.rsplit('.', 1)[0]
            nome_download = f"{nome_original}_comprimido.{extensao}"

            response = HttpResponse(buffer_saida.getvalue(), content_type=mime_type)
            response['Content-Disposition'] = f'attachment; filename="{nome_download}"'
            return response

        except Exception as e:
            return HttpResponseBadRequest(f"Erro ao comprimir imagem: {str(e)}")