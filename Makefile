build:
	docker build -t navatusein/silero-tts-service:$(v) -t navatusein/silero-tts-service:latest .
push:
	docker push navatusein/silero-tts-service -a
run:
	docker run -p 9898:9898 -m 1g --rm --name tts_silero navatusein/silero-tts-service
dev:
	make build && make run