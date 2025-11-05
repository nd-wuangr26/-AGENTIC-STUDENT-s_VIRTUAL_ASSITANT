
</p>
<p align="center"><h1 align="center">CHATBOT-RAG</h1></p>
</p>
<p align="center">
	<img src="https://img.shields.io/github/license/nd-wuangr26/RAG_QrandtDB?style=default&logo=opensourceinitiative&logoColor=white&color=0080ff" alt="license">
	<img src="https://img.shields.io/github/last-commit/nd-wuangr26/RAG_QrandtDB?style=default&logo=git&logoColor=white&color=0080ff" alt="last-commit">
	<img src="https://img.shields.io/github/languages/top/nd-wuangr26/RAG_QrandtDB?style=default&color=0080ff" alt="repo-top-language">
	<img src="https://img.shields.io/github/languages/count/nd-wuangr26/RAG_QrandtDB?style=default&color=0080ff" alt="repo-language-count">
</p>
<p align="center"><!-- default option, no dependency badges. -->
</p>
<p align="center">
	<!-- default option, no dependency badges. -->
</p>
<br>

##  Table of Contents

- [ Overview](#-overview)
- [ Features](#-features)
- [ Project Structure](#-project-structure)
  - [ Project Index](#-project-index)
- [ Getting Started](#-getting-started)
  - [ Prerequisites](#-prerequisites)
  - [ Installation](#-installation)
  - [ Usage](#-usage)
  - [ Testing](#-testing)
- [ Contributing](#-contributing)
- [ License](#-license)
- [ Acknowledgments](#-acknowledgments)

---

##  Overview

RAG_QrandtDB is an innovative system that combines retrieval-augmented generation (RAG) with the powerful Qdrant vector database to enable faster, more accurate content generation and intelligent search. This solution integrates real-time data retrieval from a scalable vector database to enhance the performance of generative AI models, making it ideal for tasks like question answering, document summarization, and personalized content generation. With a user-friendly API and high-performance architecture, RAG_QrandtDB provides a flexible and customizable solution for building advanced AI-powered systems

---

##  Features

- Real-Time Data Retrieval: Seamlessly fetches relevant data from the Qdrant database to augment the output of generative AI models, ensuring more accurate and contextually relevant responses.

- Qdrant Backend Integration: Leverages the power of Qdrant for efficient vector storage, search, and retrieval, supporting fast, high-throughput queries across large datasets.

- Augmented Language Models: Combines state-of-the-art generative models with real-time retrieval capabilities to enhance the quality and relevance of AI-generated content.

- Optimized for NLP Tasks: Perfect for use cases like question answering, content generation, summarization, and intelligent search engines.

- Scalable and High-Performance: Designed for low-latency, high-throughput applications, capable of handling large datasets and frequent queries.

- Easily Extensible and Customizable: The system is highly adaptable, allowing for easy integration with other services or modification for specific use cases.

- Simple API for Easy Integration: Provides a clean, RESTful API that simplifies interaction with the RAG model, making it easy to integrate into other projects and workflows.

- Modular Design: The project is built with a modular architecture, making it easy to extend and modify to fit a wide range of NLP applications and use cases.

---

##  Project Structure

```sh
.
├── app
│   │   
│   ├── core
│   │   ├── chunking
│   │   │   └── docling_chunk.py
│   │   ├── config
│   │   │   ├── config.py
│   │   │   └── __pycache__
│   │   │       └── config.cpython-310.pyc
│   │   ├── embeding
│   │   │   ├── base.py
│   │   │   ├── embeddings.py
│   │   │   ├── __init__.py
│   │   │   └── __pycache__
│   │   │       ├── base.cpython-310.pyc
│   │   │       ├── embeddings.cpython-310.pyc
│   │   │       └── __init__.cpython-310.pyc
│   │   ├── llm
│   │   │   ├── geminiLLM.py
│   │   │   └── __pycache__
│   │   │       └── geminiLLM.cpython-310.pyc
│   │   ├── re_renk
│   │   │   ├── core.py
│   │   │   └── __pycache__
│   │   │       └── core.cpython-310.pyc
│   │   ├── schenma
│   │   │   ├── __pycache__
│   │   │   │   └── reponse_schenma.cpython-310.pyc
│   │   │   └── reponse_schenma.py
│   │   └── vector_strore
│   │       ├── base_vectorDB.py
│   │       └── __pycache__
│   │           └── base_vectorDB.cpython-310.pyc
│   ├── db
│   │   ├── __pycache__
│   │   │   └── qdrant_service.cpython-310.pyc
│   │   └── qdrant_service.py
│   ├── __pycache__
│   │   └── server.cpython-310.pyc
│   ├── rag
│   │   ├── __pycache__
│   │   │   └── rag_core.cpython-310.pyc
│   │   └── rag_core.py
│   ├── reflection
│   │   ├── core.py
│   │   └── __pycache__
│   │       └── core.cpython-310.pyc
│   ├── save_vectordb.py
│   ├── sematic_router
│   │   ├── __pycache__
│   │   │   ├── route.cpython-310.pyc
│   │   │   ├── sample.cpython-310.pyc
│   │   │   └── sematic_route.cpython-310.pyc
│   │   ├── route.py
│   │   ├── sample.py
│   │   └── sematic_route.py
│   └── startup
│       ├── __pycache__
│       │   └── startup.cpython-310.pyc
│       └── startup.py
├── compose.yaml
├── Dockerfile
├── font-end
│   └── app.py
├── __pycache__
│   └── server.cpython-310.pyc
├── README.md
├── requirements.txt
└── server.py

```


###  Project Index
<details open>
	<summary><b><code>RAG_QRANDTDB/</code></b></summary>
	<details> <!-- __root__ Submodule -->
		<summary><b>__root__</b></summary>
		<blockquote>
			<table>
			<tr>
				<td><b><a href='https://github.com/nd-wuangr26/RAG_QrandtDB/blob/master/compose.yaml'>compose.yaml</a></b></td>
			</tr>
			<tr>
				<td><b><a href='https://github.com/nd-wuangr26/RAG_QrandtDB/blob/master/server.py'>server.py</a></b></td>
				<td><code>❯ Run back end</code></td>
			</tr>
			<tr>
				<td><b><a href='https://github.com/nd-wuangr26/RAG_QrandtDB/blob/master/requirements.txt'>requirements.txt</a></b></td>
				<td><code>❯ Install environments</code></td>
			</tr>
			<tr>
				<td><b><a href='https://github.com/nd-wuangr26/RAG_QrandtDB/blob/master/Dockerfile'>Dockerfile</a></b></td>
				<td><code>❯ Deloy Docker</code></td>
			</tr>
			</table>
		</blockquote>
	</details>
	<details> <!-- font-end Submodule -->
		<summary><b>font-end</b></summary>
		<blockquote>
			<table>
			<tr>
				<td><b><a href='https://github.com/nd-wuangr26/RAG_QrandtDB/blob/master/font-end/app.py'>app.py</a></b></td>
				<td><code>❯ Run font end</code></td>
			</tr>
			</table>
		</blockquote>
	</details>
	<details> <!-- app Submodule -->
		<summary><b>app</b></summary>
		<blockquote>
			<table>
			<tr>
				<td><b><a href='https://github.com/nd-wuangr26/RAG_QrandtDB/blob/master/app/save_vectordb.py'>save_vectordb.py</a></b></td>
				<td><code>❯ Run for save vector database</code></td>
			</tr>
			</table>
			<details>
				<summary><b>rag</b></summary>
				<blockquote>
					<table>
					<tr>
						<td><b><a href='https://github.com/nd-wuangr26/RAG_QrandtDB/blob/master/app/rag/rag_core.py'>rag_core.py</a></b></td>
					</tr>
					</table>
				</blockquote>
			</details>
			<details>
				<summary><b>core</b></summary>
				<blockquote>
					<details>
						<summary><b>chunking</b></summary>
						<blockquote>
							<table>
							<tr>
								<td><b><a href='https://github.com/nd-wuangr26/RAG_QrandtDB/blob/master/app/core/chunking/docling_chunk.py'>docling_chunk.py</a></b></td>
							</tr>
							</table>
						</blockquote>
					</details>
					<details>
						<summary><b>vector_strore</b></summary>
						<blockquote>
							<table>
							<tr>
								<td><b><a href='https://github.com/nd-wuangr26/RAG_QrandtDB/blob/master/app/core/vector_strore/base_vectorDB.py'>base_vectorDB.py</a></b></td>
							</tr>
							</table>
						</blockquote>
					</details>
					<details>
						<summary><b>config</b></summary>
						<blockquote>
							<table>
							<tr>
								<td><b><a href='https://github.com/nd-wuangr26/RAG_QrandtDB/blob/master/app/core/config/config.py'>config.py</a></b></td>
							</tr>
							</table>
						</blockquote>
					</details>
					<details>
						<summary><b>embeding</b></summary>
						<blockquote>
							<table>
							<tr>
								<td><b><a href='https://github.com/nd-wuangr26/RAG_QrandtDB/blob/master/app/core/embeding/base.py'>base.py</a></b></td>
							</tr>
							<tr>
								<td><b><a href='https://github.com/nd-wuangr26/RAG_QrandtDB/blob/master/app/core/embeding/embeddings.py'>embeddings.py</a></b></td>
							</tr>
							</table>
						</blockquote>
					</details>
					<details>
						<summary><b>llm</b></summary>
						<blockquote>
							<table>
							<tr>
								<td><b><a href='https://github.com/nd-wuangr26/RAG_QrandtDB/blob/master/app/core/llm/geminiLLM.py'>geminiLLM.py</a></b></td>
							</tr>
							</table>
						</blockquote>
					</details>
					<details>
						<summary><b>re_renk</b></summary>
						<blockquote>
							<table>
							<tr>
								<td><b><a href='https://github.com/nd-wuangr26/RAG_QrandtDB/blob/master/app/core/re_renk/core.py'>core.py</a></b></td>
							</tr>
							</table>
						</blockquote>
					</details>
					<details>
						<summary><b>schenma</b></summary>
						<blockquote>
							<table>
							<tr>
								<td><b><a href='https://github.com/nd-wuangr26/RAG_QrandtDB/blob/master/app/core/schenma/reponse_schenma.py'>reponse_schenma.py</a></b></td>
								<td><code>❯ REPLACE-ME</code></td>
							</tr>
							</table>
						</blockquote>
					</details>
				</blockquote>
			</details>
			<details>
				<summary><b>startup</b></summary>
				<blockquote>
					<table>
					<tr>
						<td><b><a href='https://github.com/nd-wuangr26/RAG_QrandtDB/blob/master/app/startup/startup.py'>startup.py</a></b></td>
					</tr>
					</table>
				</blockquote>
			</details>
			<details>
				<summary><b>reflection</b></summary>
				<blockquote>
					<table>
					<tr>
						<td><b><a href='https://github.com/nd-wuangr26/RAG_QrandtDB/blob/master/app/reflection/core.py'>core.py</a></b></td>
					</tr>
					</table>
				</blockquote>
			</details>
			<details>
				<summary><b>sematic_router</b></summary>
				<blockquote>
					<table>
					<tr>
						<td><b><a href='https://github.com/nd-wuangr26/RAG_QrandtDB/blob/master/app/sematic_router/route.py'>route.py</a></b></td>
						<td><code>❯ REPLACE-ME</code></td>
					</tr>
					<tr>
						<td><b><a href='https://github.com/nd-wuangr26/RAG_QrandtDB/blob/master/app/sematic_router/sematic_route.py'>sematic_route.py</a></b></td>
					</tr>
					<tr>
						<td><b><a href='https://github.com/nd-wuangr26/RAG_QrandtDB/blob/master/app/sematic_router/sample.py'>sample.py</a></b></td>
					</tr>
					</table>
				</blockquote>
			</details>
			<details>
				<summary><b>db</b></summary>
				<blockquote>
					<table>
					<tr>
						<td><b><a href='https://github.com/nd-wuangr26/RAG_QrandtDB/blob/master/app/db/qdrant_service.py'>qdrant_service.py</a></b></td>
					</tr>
					</table>
				</blockquote>
			</details>
		</blockquote>
	</details>
</details>

---
##  Getting Started

###  Prerequisites

Before getting started with RAG_QrandtDB, ensure your runtime environment meets the following requirements:

- **Programming Language:** Python
- **Package Manager:** Pip
- **Container Runtime:** Docker


###  Installation

Install RAG_QrandtDB using one of the following methods:

**Build Qdrant in Docker**

1. Pull the Qdrant Docker Image:
```ssh
docker pull qdrant/qdrant
```
2. Run the Qdrant Container:
```ssh
docker run -p 6333:6333 \
  -v $(pwd)/qdrant_storage:/qdrant/storage \
  qdrant/qdrant
```
After running the command, Qdrant should be accessible at **localhost:6333**

**Build from source:**

1. Clone the RAG_QrandtDB repository:
```sh
❯ git clone https://github.com/nd-wuangr26/RAG_QrandtDB
```

2. Navigate to the project directory:
```sh
❯ cd RAG_QrandtDB
```

3. Install the project dependencies:


**Using `pip`** &nbsp; [<img align="center" src="https://img.shields.io/badge/Pip-3776AB.svg?style={badge_style}&logo=pypi&logoColor=white" />](https://pypi.org/project/pip/)

```sh
❯ pip install -r requirements.txt
```
**Setup data and buid vectordb**

1. Set up URL data in core/config/config.py
2. Run Qdrant in docker
3. Run save_vectordb.py

**Using `docker`** &nbsp; [<img align="center" src="https://img.shields.io/badge/Docker-2CA5E0.svg?style={badge_style}&logo=docker&logoColor=white" />](https://www.docker.com/)

```sh
❯ docker build -t nd-wuangr26/RAG_QrandtDB .
```

###  Usage
Run RAG_QrandtDB using the following command:
**Using `pip`** &nbsp; [<img align="center" src="https://img.shields.io/badge/Pip-3776AB.svg?style={badge_style}&logo=pypi&logoColor=white" />](https://pypi.org/project/pip/)

```sh
❯ python {entrypoint}
```


**Using `docker`** &nbsp; [<img align="center" src="https://img.shields.io/badge/Docker-2CA5E0.svg?style={badge_style}&logo=docker&logoColor=white" />](https://www.docker.com/)

```sh
❯ docker run -it {image_name}
```


###  Testing

<img width="1850" height="1053" alt="Screenshot from 2025-08-12 00-52-38" src="https://github.com/user-attachments/assets/f1c68032-5adc-49cf-b7e6-61981d4682e8" />

<img width="1850" height="1053" alt="Screenshot from 2025-08-12 00-53-17" src="https://github.com/user-attachments/assets/1949c265-0721-4a97-86b4-78e7817f42b3" />


---
##  Contributing

- **💬 [Join the Discussions](https://github.com/nd-wuangr26/RAG_QrandtDB/discussions)**: Share your insights, provide feedback, or ask questions.
- **🐛 [Report Issues](https://github.com/nd-wuangr26/RAG_QrandtDB/issues)**: Submit bugs found or log feature requests for the `RAG_QrandtDB` project.
- **💡 [Submit Pull Requests](https://github.com/nd-wuangr26/RAG_QrandtDB/blob/main/CONTRIBUTING.md)**: Review open PRs, and submit your own PRs.

<details open>
<summary>Contributing Guidelines</summary>

1. **Fork the Repository**: Start by forking the project repository to your github account.
2. **Clone Locally**: Clone the forked repository to your local machine using a git client.
   ```sh
   git clone https://github.com/nd-wuangr26/RAG_QrandtDB
   ```
3. **Create a New Branch**: Always work on a new branch, giving it a descriptive name.
   ```sh
   git checkout -b new-feature-x
   ```
4. **Make Your Changes**: Develop and test your changes locally.
5. **Commit Your Changes**: Commit with a clear message describing your updates.
   ```sh
   git commit -m 'Implemented new feature x.'
   ```
6. **Push to github**: Push the changes to your forked repository.
   ```sh
   git push origin new-feature-x
   ```
7. **Submit a Pull Request**: Create a PR against the original project repository. Clearly describe the changes and their motivations.
8. **Review**: Once your PR is reviewed and approved, it will be merged into the main branch. Congratulations on your contribution!
</details>

<details open>
<summary>Contributor Graph</summary>
<br>
<p align="left">
   <a href="https://github.com{/nd-wuangr26/RAG_QrandtDB/}graphs/contributors">
      <img src="https://contrib.rocks/image?repo=nd-wuangr26/RAG_QrandtDB">
   </a>
</p>
</details>

---

##  License

This project is protected under the [SELECT-A-LICENSE](https://choosealicense.com/licenses) License. For more details, refer to the [LICENSE](https://choosealicense.com/licenses/) file.

---

##  Acknowledgments

- List any resources, contributors, inspiration, etc. here.

---
