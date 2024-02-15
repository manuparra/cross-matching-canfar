image:
	@docker build . --tag cross-matching:latest

image-jupyter:
	@docker build . -f jupyter/Dockerfile --tag cross-matching-jupyter:latest

run:
	@docker pull registry.gitlab.com/ska-telescope/src/src-workloads/cross-matching:latest
	@docker run -it --rm --name cross-matching -t -v "$(pwd)"/scripts:/scripts/ registry.gitlab.com/ska-telescope/src/src-workloads/cross-matching:latest

run-local:
	@docker run -it --rm --name cross-matching -v "$(pwd)"/scripts:/scripts/ cross-matching:latest

run-local-jupyter:
	@docker run -it --rm --name cross-matching-jupyter -p 8888:8888 cross-matching-jupyter:latest
