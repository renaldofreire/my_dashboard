# my_dashboard — Resumo do Projeto

## O que é

Dashboard pessoal auto-hospedado, acessível em `dashboard.charisrv.fyi`.
Página única que agrega informações úteis do cotidiano: mercado financeiro,
clima, atividade no GitHub e tecnologia — tudo atualizado automaticamente,
sem precisar abrir múltiplos sites.

---

## Stack

| Camada | Tecnologia | Motivo |
|---|---|---|
| Linguagem | Python 3 | Foco principal do projeto |
| Backend | Flask 3 | Leve, direto, sem overhead |
| Templates | Jinja2 | Nativo do Flask |
| Frontend dinâmico | HTMX | Refresh parcial de cards sem JavaScript framework |
| Cache | cachetools (TTLCache) | Evita excesso de requisições às APIs externas |
| HTTP client | requests | Simples e estável |
| Estilo | CSS puro + IBM Plex Mono/Sans | Estética terminal/industrial, sem framework CSS |
| Infra | Proxmox LXC (Debian 12) | Container leve, sem overhead de VM |
| Processo | systemd | Gerenciamento nativo do serviço Flask |
| Exposição | Cloudflare Tunnel | HTTPS automático, sem abrir portas no roteador |
| Versionamento | Git + GitHub | Controle de versão e portfólio |

---

## Arquitetura

```
Arch Linux (dev)
      │
      │  git push
      ▼
   GitHub
      │
      │  git pull
      ▼
Proxmox LXC — Debian 12
  /opt/my_dashboard
  └── Flask (porta 5000)
        │
        │  systemd (dashboard.service)
        ▼
  Cloudflare Tunnel
        │
        ▼
  dashboard.charisrv.fyi
```

**Fluxo de deploy:**
```bash
# Desenvolve local no Arch, testa, sobe para o GitHub
git push

# No LXC, atualiza e reinicia
cd /opt/my_dashboard && git pull && systemctl restart dashboard
```

---

## Estrutura de pastas

```
my_dashboard/
├── app/
│   ├── __init__.py          # App factory do Flask
│   ├── routes.py            # Todas as rotas e endpoints da API
│   └── widgets/
│       ├── __init__.py
│       ├── crypto.py        # Bitcoin + câmbio
│       ├── hackernews.py    # HN top 5
│       ├── weather.py       # Clima (OpenMeteo)
│       ├── github_activity.py  # GitHub Events API
│       └── football.py      # Em desenvolvimento
├── templates/
│   └── index.html           # Template único com HTMX
├── static/
│   └── style.css            # Estilo do dashboard
├── config.py                # Configurações e TTL de cache
├── requirements.txt
└── run.py                   # Entry point
```

---

## Widgets implementados

### Bitcoin / USD
- **Fonte:** CoinGecko API
- **Auth:** nenhuma
- **Cache:** 5 minutos
- **Exibe:** preço atual do BTC em USD

### Câmbio
- **Fonte:** frankfurter.app
- **Auth:** nenhuma
- **Cache:** 5 minutos
- **Exibe:** USD → BRL e GBP → BRL

### Clima — Fortaleza / Maracanaú
- **Fonte:** Open-Meteo
- **Auth:** nenhuma
- **Cache:** 10 minutos
- **Exibe:** temperatura atual, condição, máxima/mínima, probabilidade de chuva
- **Detalhe:** badge dedicado "vai chover hoje" / "sem chuva prevista"
- **Toggle:** troca entre Fortaleza e Maracanaú sem recarregar a página

### GitHub Activity
- **Fonte:** GitHub Events API (pública)
- **Auth:** nenhuma
- **Cache:** 10 minutos
- **Exibe:** últimos 6 eventos públicos — push, PR, issue, create, fork, star

### Hacker News Top 5
- **Fonte:** HN Firebase API
- **Auth:** nenhuma
- **Cache:** 10 minutos
- **Exibe:** top 5 stories com título, link e pontuação
- **Detalhe:** requests paralelas com `concurrent.futures` para buscar os 5 itens simultaneamente

---

## Problemas resolvidos durante o desenvolvimento

**Cache collision (crypto.py)**
Duas funções sem argumentos (`get_bitcoin_price` e `get_exchange_rates`)
compartilhavam o mesmo objeto `TTLCache`. Como a chave de cache é derivada
dos argumentos da função, ambas geravam a mesma chave `()` e colidiam —
a segunda sempre retornava o valor da primeira. Solução: uma instância de
cache separada por função.

**Toggle de cidade travado no "carregando"**
O toggle usava `htmx.trigger()` após modificar o atributo `hx-get`
dinamicamente. O handler `htmx:afterRequest` não capturava corretamente
porque o elemento disparador e o alvo da requisição divergiam. Solução:
substituir por `fetch()` assíncrono direto, extraindo a função `renderWeather()`
para reuso tanto pelo HTMX (carga inicial) quanto pelo toggle manual.

**Contagem de commits zerada (GitHub)**
A GitHub Events API retorna o campo `size` no payload do `PushEvent` para
indicar o número de commits — não o tamanho do array `commits`, que pode
vir vazio em eventos públicos. Solução: usar `payload.get("size")` como
valor primário com fallback para `len(commits)`.

---

## Próximos passos

### Widget: Futebol
- **Times:** Flamengo · Manchester United · Borussia Dortmund
- **Fonte:** Free API Live Football Data (RapidAPI) — API key obtida
- **Exibe:** resultado do último jogo + próximo adversário
- **Cache:** 30 minutos (dado de baixa variação)

### Widget: Status do Proxmox
- Verificação de conectividade do servidor com a internet
- Request HTTP para `1.1.1.1` com medição de latência
- Exibe: online/offline + latência em ms

### Melhorias técnicas planejadas
- Migrar de Flask dev server para **Gunicorn** (WSGI de produção)
- Adicionar `.env` para variáveis sensíveis (API keys) com `python-dotenv`
- Página de erro customizada (404 / 500)
- Favicon

### Melhorias de interface planejadas
- Timestamp do último update em cada card
- Indicador visual de "atualizando" durante o refresh do HTMX
- Modo responsivo refinado para mobile

---

## APIs utilizadas

| API | URL | Auth | Limite free |
|---|---|---|---|
| CoinGecko | `api.coingecko.com` | Nenhuma | ~30 req/min |
| Frankfurter | `api.frankfurter.app` | Nenhuma | Sem limite documentado |
| Open-Meteo | `api.open-meteo.com` | Nenhuma | 10.000 req/dia |
| HN Firebase | `hacker-news.firebaseio.com` | Nenhuma | Sem limite documentado |
| GitHub Events | `api.github.com` | Nenhuma (público) | 60 req/hora |
| Free Football API | `rapidapi.com` | API key | 100 req/dia |

---

## Motivação

Projeto construído para consolidar habilidades em Python/Flask, consumo de
APIs REST, deploy self-hosted e boas práticas de versionamento com Git.
Faz parte do portfólio em transição para desenvolvimento de software,
complementando experiência profissional em qualidade e processos.

Repositório: `github.com/renaldofreire/my_dashboard`