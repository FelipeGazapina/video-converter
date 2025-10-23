# Conversor de Vídeo - Interface Web

Uma interface web moderna e intuitiva para conversão, compressão e extração de áudio de arquivos de vídeo usando FFmpeg.

## Funcionalidades

- **Converter MKV → MP4**: Converte arquivos MKV para MP4 mantendo a qualidade do vídeo
- **Comprimir MP4**: Reduz o tamanho de arquivos MP4 usando compressão H.264
- **Extrair MP3**: Extrai áudio de vídeos e salva como MP3 com qualidade máxima
- **Interface Drag & Drop**: Interface moderna com upload por arrastar e soltar
- **Visualização de Resultados**: Página dedicada para visualizar e baixar arquivos processados
- **Processamento Assíncrono**: Processamento em background com atualizações de status em tempo real

## Pré-requisitos

- Python 3.7+
- FFmpeg instalado no sistema

### Instalação do FFmpeg

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install -y ffmpeg
```

**CentOS/RHEL:**
```bash
sudo yum install epel-release
sudo yum install ffmpeg
```

**macOS (com Homebrew):**
```bash
brew install ffmpeg
```

**Windows:**
Baixe de https://ffmpeg.org/download.html e adicione ao PATH

## Instalação

1. Clone ou baixe este repositório
2. Instale as dependências:
```bash
pip install -r requirements.txt
```

## Uso

1. Execute a aplicação:
```bash
python app.py
```

2. Abra seu navegador e acesse: `http://localhost:5000`

3. Use a interface para:
   - Selecionar um arquivo de vídeo (arrastar e soltar ou clicar para selecionar)
   - Escolher a operação desejada
   - Aguardar o processamento
   - Visualizar e baixar os resultados na página de resultados

## Estrutura do Projeto

```
/workspace/
├── app.py                 # Aplicação Flask principal
├── convert_video.py       # Script original de conversão
├── requirements.txt       # Dependências Python
├── README.md             # Este arquivo
├── templates/            # Templates HTML
│   ├── base.html         # Template base
│   ├── index.html        # Página principal
│   └── results.html      # Página de resultados
├── uploads/              # Arquivos enviados (criado automaticamente)
└── output/               # Arquivos processados (criado automaticamente)
    ├── mp4/              # Arquivos MP4 convertidos
    ├── mp4/compressed/   # Arquivos MP4 comprimidos
    └── mp3/              # Arquivos MP3 extraídos
```

## Características Técnicas

- **Backend**: Flask com processamento assíncrono
- **Frontend**: HTML5, CSS3, JavaScript (jQuery)
- **Upload**: Suporte a drag & drop com validação de tipos
- **Processamento**: FFmpeg via subprocess
- **Interface**: Design responsivo e moderno
- **Status**: Atualizações em tempo real via AJAX

## Limitações

- Tamanho máximo de arquivo: 500MB
- Formatos suportados: MP4, MKV, AVI, MOV e outros formatos suportados pelo FFmpeg
- Processamento sequencial (um arquivo por vez)

## Solução de Problemas

### FFmpeg não encontrado
Se você receber o erro "FFmpeg não encontrado", certifique-se de que o FFmpeg está instalado e disponível no PATH do sistema.

### Erro de permissão
Certifique-se de que a aplicação tem permissão para criar as pastas `uploads` e `output`.

### Arquivo muito grande
O limite padrão é 500MB. Para aumentar, modifique `MAX_CONTENT_LENGTH` no arquivo `app.py`.

## Desenvolvimento

Para executar em modo de desenvolvimento:
```bash
export FLASK_ENV=development
python app.py
```

## Licença

Este projeto é de código aberto e está disponível sob a licença MIT.