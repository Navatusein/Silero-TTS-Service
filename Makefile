build:
	docker build -t navatusein/silero-tts-service .
push:
	docker push navatusein/silero-tts-service:latest
run:
	docker run -p 9898:9898 --rm --name tts_silero navatusein/silero-tts-service
dev:
	make build && make run