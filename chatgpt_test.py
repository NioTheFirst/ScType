import openai

openai.api_key = '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'


messages = [ {"role": "system", "content": "You will add the word 'chicken' in front of every response."} ]
TEST = False
if(TEST):
	while True:
		message = input("User : ")
		if message:
			messages.append(
				{"role": "user", "content": message},
			)
			chat = openai.ChatCompletion.create(
				model="gpt-3.5-turbo", messages=messages
			)

		reply = chat.choices[0].message.content
		print(f"ChatGPT: {reply}")
		messages.append({"role": "assistant", "content": reply})

all_prompts = {}
all_prompts

