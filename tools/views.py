import io
import numpy as np
import zipfile
from PIL import Image
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseBadRequest


def home_view(request):
    return render(request, 'tools/home.html')


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


def remover_fundo_view(request):
    if request.method == 'GET':
        return render(request, 'tools/background_remover.html')

    if request.method == 'POST':
        arquivo = request.FILES.get('imagem')
        tolerancia = int(request.POST.get('tolerancia', 35))

        if not arquivo:
            return HttpResponseBadRequest("Nenhum ficheiro enviado.")

        try:
            # 1. Carrega a imagem para memória
            img = Image.open(arquivo).convert("RGBA")
            dados = np.array(img)

            # 2. Identifica a cor dos cantos superiores para definir a cor do fundo
            cor_fundo = dados[0, 0, :3]

            # 3. Calcula a distância cromática de cada píxel em relação ao fundo
            r, g, b, a = dados[:, :, 0], dados[:, :, 1], dados[:, :, 2], dados[:, :, 3]
            distancia = np.sqrt(
                (r.astype(int) - int(cor_fundo[0])) ** 2 +
                (g.astype(int) - int(cor_fundo[1])) ** 2 +
                (b.astype(int) - int(cor_fundo[2])) ** 2
            )

            # 4. Transforma em transparente os píxeis que coincidem com a cor de fundo
            mascara = distancia < tolerancia
            dados[mascara, 3] = 0

            # 5. Gera o ficheiro PNG resultante em RAM
            img_resultado = Image.fromarray(dados)
            buffer_saida = io.BytesIO()
            img_resultado.save(buffer_saida, format="PNG", optimize=True)
            buffer_saida.seek(0)

            nome_original = arquivo.name.rsplit('.', 1)[0]
            nome_download = f"{nome_original}_sem_fundo.png"

            response = HttpResponse(buffer_saida.getvalue(), content_type="image/png")
            response['Content-Disposition'] = f'attachment; filename="{nome_download}"'
            return response

        except Exception as e:
            return HttpResponseBadRequest(f"Falha ao remover fundo: {str(e)}")


def redimensionar_view(request):
    if request.method == 'GET':
        return render(request, 'tools/image_resizer.html')

    if request.method == 'POST':
        arquivo = request.FILES.get('imagem')
        largura = request.POST.get('largura')
        altura = request.POST.get('altura')
        manter_proporcao = request.POST.get('manter_proporcao') == 'on'

        if not arquivo:
            return HttpResponseBadRequest("Nenhum ficheiro enviado.")

        try:
            largura = int(largura) if largura else None
            altura = int(altura) if altura else None
        except ValueError:
            return HttpResponseBadRequest("Valores de dimensões inválidos.")

        if not largura and not altura:
            return HttpResponseBadRequest("Indique pelo menos uma dimensão (largura ou altura).")

        try:
            img = Image.open(arquivo)
            largura_orig, altura_orig = img.size

            # Cálculo de proporção caso apenas uma dimensão seja indicada ou a caixa esteja ativa
            if manter_proporcao:
                if largura and not altura:
                    proporcao = largura / float(largura_orig)
                    altura = int(float(altura_orig) * float(proporcao))
                elif altura and not largura:
                    proporcao = altura / float(altura_orig)
                    largura = int(float(largura_orig) * float(proporcao))
                elif largura and altura:
                    proporcao = min(largura / float(largura_orig), altura / float(altura_orig))
                    largura = int(float(largura_orig) * float(proporcao))
                    altura = int(float(altura_orig) * float(proporcao))
            else:
                largura = largura or largura_orig
                altura = altura or altura_orig

            # Redimensionamento com filtro Lanczos de alta qualidade
            img_redimensionada = img.resize((largura, altura), Image.Resampling.LANCZOS)

            formato_saida = img.format if img.format in ('JPEG', 'PNG', 'WEBP') else 'JPEG'
            buffer_saida = io.BytesIO()

            if formato_saida == 'JPEG':
                if img_redimensionada.mode != 'RGB':
                    img_redimensionada = img_redimensionada.convert('RGB')
                img_redimensionada.save(buffer_saida, format='JPEG', quality=90, optimize=True)
                mime_type = 'image/jpeg'
                extensao = 'jpg'
            elif formato_saida == 'PNG':
                img_redimensionada.save(buffer_saida, format='PNG', optimize=True)
                mime_type = 'image/png'
                extensao = 'png'
            else:
                img_redimensionada.save(buffer_saida, format='WEBP', quality=90)
                mime_type = 'image/webp'
                extensao = 'webp'

            buffer_saida.seek(0)
            nome_original = arquivo.name.rsplit('.', 1)[0]
            nome_download = f"{nome_original}_{largura}x{altura}.{extensao}"

            response = HttpResponse(buffer_saida.getvalue(), content_type=mime_type)
            response['Content-Disposition'] = f'attachment; filename="{nome_download}"'
            return response

        except Exception as e:
            return HttpResponseBadRequest(f"Falha ao redimensionar imagem: {str(e)}")


def imagem_para_pdf_view(request):
    if request.method == 'GET':
        return render(request, 'tools/image_to_pdf.html')

    if request.method == 'POST':
        ficheiros = request.FILES.getlist('imagens')

        if not ficheiros:
            return HttpResponseBadRequest("Nenhum ficheiro enviado.")

        try:
            lista_imagens = []

            for f in ficheiros:
                img = Image.open(f)
                # Conversão obrigatória para RGB para suporte a PDF no Pillow
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                lista_imagens.append(img)

            buffer_saida = io.BytesIO()
            primeira_imagem = lista_imagens[0]
            restantes = lista_imagens[1:] if len(lista_imagens) > 1 else []

            # Compilação das páginas no buffer de memória
            primeira_imagem.save(
                buffer_saida,
                format='PDF',
                save_all=True,
                append_images=restantes
            )

            buffer_saida.seek(0)
            nome_download = "documento_convertido.pdf"

            response = HttpResponse(buffer_saida.getvalue(), content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="{nome_download}"'
            return response

        except Exception as e:
            return HttpResponseBadRequest(f"Falha ao gerar PDF: {str(e)}")


def gerador_favicon_view(request):
    if request.method == 'GET':
        return render(request, 'tools/favicon_generator.html')

    if request.method == 'POST':
        arquivo = request.FILES.get('imagem')

        if not arquivo:
            return HttpResponseBadRequest("Nenhum ficheiro enviado.")

        try:
            img = Image.open(arquivo)

            # 1. Garantir transparência/RGBA
            if img.mode != 'RGBA':
                img = img.convert('RGBA')

            # 2. Fazer recorte central quadrado para não distorcer o ícone
            largura, altura = img.size
            lado_minimo = min(largura, altura)
            esquerda = (largura - lado_minimo) // 2
            topo = (altura - lado_minimo) // 2
            img_quadrada = img.crop((esquerda, topo, esquerda + lado_minimo, topo + lado_minimo))

            # 3. Criar arquivo ZIP em memória RAM
            buffer_zip = io.BytesIO()

            with zipfile.ZipFile(buffer_zip, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                # Gerar o favicon.ico padrão multirresolução (16x16, 32x32, 48x48)
                buffer_ico = io.BytesIO()
                img_quadrada.save(
                    buffer_ico,
                    format='ICO',
                    sizes=[(16, 16), (32, 32), (48, 48)]
                )
                zip_file.writestr('favicon.ico', buffer_ico.getvalue())

                # Tamanhos individuais em PNG
                tamanhos_png = {
                    'favicon-16x16.png': (16, 16),
                    'favicon-32x32.png': (32, 32),
                    'apple-touch-icon.png': (180, 180),
                    'android-chrome-192x192.png': (192, 192),
                    'android-chrome-512x512.png': (512, 512),
                }

                for nome_png, dimensao in tamanhos_png.items():
                    buffer_png = io.BytesIO()
                    img_redimensionada = img_quadrada.resize(dimensao, Image.Resampling.LANCZOS)
                    img_redimensionada.save(buffer_png, format='PNG', optimize=True)
                    zip_file.writestr(nome_png, buffer_png.getvalue())

                # Snippet de tags HTML
                snippet_tags = (
                    '<link rel="icon" type="image/x-icon" href="/favicon.ico">\n'
                    '<link rel="icon" type="image/png" sizes="16x16" href="/favicon-16x16.png">\n'
                    '<link rel="icon" type="image/png" sizes="32x32" href="/favicon-32x32.png">\n'
                    '<link rel="apple-touch-icon" sizes="180x180" href="/apple-touch-icon.png">\n'
                    '<link rel="icon" type="image/png" sizes="192x192" href="/android-chrome-192x192.png">\n'
                    '<link rel="icon" type="image/png" sizes="512x512" href="/android-chrome-512x512.png">'
                )

                # Página HTML visual formatada para abrir no navegador
                pagina_html = f"""<!DOCTYPE html>
<html lang="pt">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Instruções - Kit de Favicons</title>
  <style>
    * {{ box-sizing: border-box; }}
    body {{
      font-family: monospace;
      background-color: #F8F9FA;
      color: #000;
      padding: 40px 20px;
      margin: 0;
      display: flex;
      justify-content: center;
    }}
    .container {{
      max-width: 760px;
      width: 100%;
      background: #fff;
      border: 4px solid #000;
      box-shadow: 8px 8px 0px #000;
      padding: 32px;
    }}
    .badge {{
      display: inline-block;
      background: #FFE600;
      color: #000;
      font-weight: 900;
      padding: 6px 12px;
      border: 2px solid #000;
      box-shadow: 3px 3px 0 #000;
      text-transform: uppercase;
      margin-bottom: 16px;
    }}
    h1 {{
      font-size: 28px;
      font-weight: 900;
      text-transform: uppercase;
      margin: 0 0 12px 0;
    }}
    p {{
      font-size: 14px;
      line-height: 1.6;
      color: #333;
      margin: 8px 0;
    }}
    pre {{
      background: #111;
      color: #00FF66;
      border: 3px solid #000;
      padding: 16px;
      font-size: 13px;
      overflow-x: auto;
      line-height: 1.5;
      margin-top: 16px;
    }}
  </style>
</head>
<body>
  <div class="container">
    <div class="badge">ToolsHub Favicon Kit</div>
    <h1>Como Utilizar os Ícones</h1>
    <p><strong>1.</strong> Copie todos os ficheiros de imagem gerados para a pasta pública ou raiz do seu sítio web.</p>
    <p><strong>2.</strong> Adicione o seguinte bloco de código dentro da secção <code>&lt;head&gt;</code> do seu HTML:</p>
    <pre><code>{snippet_tags.replace('<', '&lt;').replace('>', '&gt;')}</code></pre>
  </div>
</body>
</html>"""

                zip_file.writestr('instrucoes_html.html', pagina_html)
                zip_file.writestr('instrucoes.txt', f"COPIE ESTE CODIGO PARA A TAG <head> DO SEU SITE:\n\n{snippet_tags}\n")

            buffer_zip.seek(0)
            nome_download = "favicon_kit.zip"

            response = HttpResponse(buffer_zip.getvalue(), content_type='application/zip')
            response['Content-Disposition'] = f'attachment; filename="{nome_download}"'
            return response

        except Exception as e:
            return HttpResponseBadRequest(f"Erro ao gerar favicons: {str(e)}")


def cortar_imagem_view(request):
    if request.method == 'GET':
        return render(request, 'tools/image_cropper.html')

    if request.method == 'POST':
        arquivo = request.FILES.get('imagem')

        try:
            x = float(request.POST.get('x', 0))
            y = float(request.POST.get('y', 0))
            largura = float(request.POST.get('width', 0))
            altura = float(request.POST.get('height', 0))
        except (TypeError, ValueError):
            return HttpResponseBadRequest("Coordenadas de corte inválidas.")

        if not arquivo:
            return HttpResponseBadRequest("Nenhum ficheiro enviado.")

        if largura <= 0 or altura <= 0:
            return HttpResponseBadRequest("A área de corte deve ter dimensões maiores que zero.")

        try:
            img = Image.open(arquivo)

            # Define a caixa de corte (left, upper, right, lower)
            box = (int(x), int(y), int(x + largura), int(y + altura))
            img_cortada = img.crop(box)

            formato_saida = img.format if img.format in ('JPEG', 'PNG', 'WEBP') else 'JPEG'
            buffer_saida = io.BytesIO()

            if formato_saida == 'JPEG':
                if img_cortada.mode != 'RGB':
                    img_cortada = img_cortada.convert('RGB')
                img_cortada.save(buffer_saida, format='JPEG', quality=90, optimize=True)
                mime_type = 'image/jpeg'
                extensao = 'jpg'
            elif formato_saida == 'PNG':
                img_cortada.save(buffer_saida, format='PNG', optimize=True)
                mime_type = 'image/png'
                extensao = 'png'
            else:
                img_cortada.save(buffer_saida, format='WEBP', quality=90)
                mime_type = 'image/webp'
                extensao = 'webp'

            buffer_saida.seek(0)
            nome_original = arquivo.name.rsplit('.', 1)[0]
            nome_download = f"{nome_original}_recortado.{extensao}"

            response = HttpResponse(buffer_saida.getvalue(), content_type=mime_type)
            response['Content-Disposition'] = f'attachment; filename="{nome_download}"'
            return response

        except Exception as e:
            return HttpResponseBadRequest(f"Falha ao cortar imagem: {str(e)}")