# Hackaton - API de Ingestão de Vídeos

## Sobre o Projeto
O **Hack Video Ingest** é uma API responsável por realizar a ingestão de vídeos no sistema. Construída em Python utilizando o framework FastAPI, este microsserviço recebe os vídeos enviados pelos usuários, realiza o upload seguro para um bucket no Amazon S3, salva os metadados da operação no Amazon DynamoDB e enfileira uma mensagem no Amazon SQS para que os workers realizem o processamento assíncrono do vídeo.

## Tecnologias Utilizadas
- **Linguagem Principal**: Python 3.10
- **Framework Web**: FastAPI (com Uvicorn)
- **Cloud Provider AWS**: S3 (Storage), SQS (Filas de Mensageria), DynamoDB (Banco de Dados NoSQL), ECR (Container Registry), EKS (Kubernetes)
- **Infraestrutura e Containers**: Docker, Docker Compose, Kubernetes, Kustomize
- **CI/CD**: GitHub Actions
- **Bibliotecas**: `boto3` para integração AWS, `pydantic` para validação de esquemas, `watchtower` e `python-json-logger` para logs estruturados.

## Esteira CI/CD
A automação de integração e entrega contínua é feita através do **GitHub Actions**. O pipeline é disparado automaticamente a cada push na branch `main` ou via `workflow_dispatch` (execução manual) e consiste nas seguintes etapas (jobs):

1. **Teste e Lint (Python)**: Realiza o checkout do código, configura o Python, instala dependências e executa análises de qualidade de código (Lint) e testes unitários.
2. **Build e Push (Amazon ECR)**: Após os testes serem aprovados, o sistema constrói a imagem Docker da aplicação e a envia para o Amazon Elastic Container Registry (ECR), versionando a imagem com o hash do commit (`github.sha`) e com a tag `latest`.
3. **Deploy no EKS**: Por fim, a imagem atualizada no ECR é implantada no cluster Kubernetes da AWS (EKS). A ferramenta **Kustomize** é usada de forma dinâmica para plugar a tag nova na imagem final, substituindo variáveis e aplicando as mudanças na infraestrutura.

## Proteção da Branch Main no GitHub
Para garantir a qualidade, integridade e estabilidade do código em produção, a branch `main` é devidamente protegida contra edições diretas e quebras de código. Para integrar código ao projeto:
- **Nenhum commit direto**: É bloqueado o push direto na branch `main`. Todo desenvolvimento deve acontecer em branches separadas e integrado via **Pull Requests (PRs)**.
- **Revisão Obrigatória**: Os pull requests devem passar pela aprovação de no mínimo um Code Reviewer antes de serem mesclados.
- **Status Checks Obrigatórios**: Somente PRs que passem com sucesso nas rotinas automáticas de CI (Testes Unitários e Lint / Quality Gates) são elegíveis ao merge, impedindo que regressões ou bugs óbvios cheguem em produção.

## Melhores Práticas Adotadas
O projeto adota fortes princípios de arquitetura de software e resiliência:

- **Fair Queuing (Garantia de Equivalência e Mitigação de Noisy Neighbor)**: O sistema foi projetado para evitar que um único usuário sobrecarregue a infraestrutura ("Noisy Neighbor"). Um limite de restrição foi imposto, permitindo que cada usuário tenha, no máximo, **5 vídeos sendo processados simultaneamente**. Qualquer vídeo adicional permanece `QUEUED` no banco até que slots de processamento sejam liberados.
- **Arquitetura Limpa / Use Cases**: Isolamento das regras de negócios das camadas de infraestrutura, com o fluxo principal ocorrendo dentro das "Use Cases" (ex: `ConfirmUploadUseCase`).
- **Logs Estruturados e Correlation IDs**: Implementação de logs em formato JSON e com *Correlation IDs* atrelados aos *task_ids*. Dessa maneira, toda a jornada do vídeo, desde a API de ingestão até as filas, pode ser rastreada centralmente e facilmente depurada no Amazon CloudWatch usando ferramentas como Elasticsearch/Kibana ou o próprio painel da AWS.

## Uso do Kubernetes (K8s)
O ambiente produtivo se baseia na orquestração pelo **Amazon EKS**. Foram mapeados manifestos específicos (encontrados na pasta `/k8s/`):
- **Deployment**: Mantém os pods da aplicação rodando com alta disponibilidade.
- **HPA (Horizontal Pod Autoscaler)**: O ecossistema escala os pods horizontalmente baseado no consumo de CPU e Memória, garantindo responsividade quando os picos de ingestão aumentarem.
- **Service & Ingress**: Fornecem pontos de acesso externos da aplicação para comunicação com APIs Front-End (recebendo requisições HTTP e roteando).
- **ConfigMaps e Secrets**: Segregam variáveis vitais e chaves de segurança (KMS, senhas) fora do repositório, garantindo conformidade com regras de DevSecOps.
- **Kustomize**: Facilita a variação de ambientes (Base + Overlays) sobreescrevendo propriedades customizadas do Kubernetes a cada deploy sem repetição de código.

## Executando Localmente
Para usar o ambiente via Docker Compose com *hot-reload*:
1. Instale o Docker e o Docker Compose.
2. Clone o repositório.
3. Cadastre suas variáveis de ambiente copiando o arquivo `.env.example` para `.env`.
4. Rode as instâncias com o comando:
   ```bash
   docker-compose up --build
   ```
5. Acesse a documentação online via Swagger em `http://localhost:8000/docs`.