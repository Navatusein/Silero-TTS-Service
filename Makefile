build:
	docker build -t navatusein/silero-ha-http-tts .
push:
	docker push navatusein/silero-ha-http-tts:latest
run:
	docker run -p 9898:9898 --rm --name tts_silero navatusein/silero-ha-http-tts
dev:
	make build && make run