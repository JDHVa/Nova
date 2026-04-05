NOVA:

A LLM MedicChatBot, here you can ask anything if you have a disease or anyother kind of ailment, the feutures of the proyect are

- ChatBot potenced by Gemini, Claude and Grok
- An analyzer for x-ray's, made with the model DenseNet121 maden in PyTorch
- A public website that you can visit in this url: https://huggingface.co/spaces/JDHVa/NOVA
- IMPORTANT It's probably that if you want to use the website it might take like 2min-4min, because every 48h the website doesn't have anykind of request it unstart so  it's probably that you have to wait (If you are wondering about how is it even possible that a website use 3 or 5 minutes to launch, remember in this project we use PyTorch that is a Neuronal Network, and in the case that i using DenseNet121, this is a CNN so it's normal because think about it, the model have to train, have to test, and then it have to be launched in the website so that is the reason because it may take 3-5 minutes to launch)

Cases of Use 

1. Want to know what's going on with your own body
2. Want to know what you can o can't do in your situation
3. Know much does a medicine cust in your city
4. Want to see the result of a x-ray without going with a doctor (Disclaimer: This project is only trained by me and a repository of the web so the model may have some mistakes so dont fully trust the result)

Logic of the project since scratch

Backend

1. backend/app.py, all start here, i use FastAPI so all the logic behind the projet is directed by FastAPI, it contains methods to connect with chat_serice.py and xray_analyzer.py, so here you can see like i say all the logic behinds, all the routes and functions (made by me)
2. backend/chat_service.py, is where the logic of the LLM MedicChatBot, makes sense, here you can see the classes of the messages, and the logic behind trying to connect to the different models that we are using like Gemini, Claude, Groq, also here you can see the prompt that the ChatBot, is going to use to comunicate with the people (made by me, but the propts gemini, help me with the prompts to do it in the best way possible, so that is the reason that it may looks to long)
3. backend/xray_analyzer.py, is where the logic behind the xray analyzer works, here you'll the diseases, this helps the model to know that what kind of disease is going to try to detect, and the descriptions of each disease, then you will see as function that helps determinating the severity of each x-ray, this works with the accuracy of the model, then all the class for the x-ray, is here, all the process, since turning the image into grey-scale, to normalizing all the data, then we have the function analyze, that is were i use the model to classificate eache image with information, in english and spanish, and specifing what does the function returns (made by me, but he description of the diseases is pure Gemini)


Frontend

1. frontend/index.html, all the information and the text is shown here, all the buttons and all the thins that you can do, is only here (made my me) 
2. css/styles.css, is the design of the project all the things that you think looks good was made by CSS(made in 92% by me, the 8%, are credits for the AI, because it helps me with the idea for the design, and also it help with the color palette, also it develops the .finding-bar, because i send an image of my project and GEMINI tell me to add that fancy design and develop for me)
3. js/main.js, is where the buttons of the project know have logic, it helps making that a button like "send", really send the message to chat_service.py, it manages the logic behind the html. (made by me, but the particles animation is by a video of youtube that i see in the past and i have been using to much time)

Summarize of what do AI done and have i done

ME: 

Make all the logic behind the project all the .py files, and almost all the design of the website.

AI:

Give me an idea of what could be the design of the project, and give me the colors to use, also it helps with the particles i the website, and helps me with all the Dockerfile.

Installation if you want to try in your own computer

Hello, so first of all if you want to test the project in your own computer or maybe make changes to the code, you have to create your own venv, so here is the terminal code:

python -m venv venv

Then install all the dependecies, you can see the dependencies in the requirements.txt so see it if you want it, but in case that you see it or dont wnat to see it here is the command to install it:

pip install -r requirements.txt

Then if you want to try on your computer you have to make a .env file in the backend file the path have to be like this:

backend/.env

In that file you have to put your api key's in like this:


- -gemini=Aiza....   (YOUR GEMINI API KEY Without "" only text)

- -claude=asdfa.... (YOUR CLAUDE API KEY Without "" only text)

- -groq=gsdfgs.... (YOUR GROQ API KEY Without "" only text)

(Here is the link to have your own gemini key: https://aistudio.google.com/prompts/new_chat)

(Here is the link to have your own claude key: https://platform.claude.com/dashboard)

(Here is the link to have your own groq key: https://console.groq.com/home)

Then i think that it's all if you want to try it by your own way
