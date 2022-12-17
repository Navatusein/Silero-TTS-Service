build:
	docker build -t navatusein/Silero-TTS-Service .
push:
	docker push navatusein/Silero-TTS-Service:latest
run:
	docker run -p 9898:9898 --rm --name tts_silero navatusein/Silero-TTS-Service
dev:
	make build && make run