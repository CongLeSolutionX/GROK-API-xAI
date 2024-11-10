
import OpenAI from "openai";
import dotenv from 'dotenv';

dotenv.config({ path: '../.env' }); // since my .env file is up one directory level

// Print out environment variable to verify they are loaded
console.log(process.env.XAI_API_KEY);

const openai = new OpenAI({
  apiKey: process.env.XAI_API_KEY,
  baseURL: "https://api.x.ai/v1",
});

const completion = await openai.chat.completions.create({
  model: "grok-beta",
  messages: [
    { role: "system", content: "You are Grok, a chatbot inspired by the Hitchhiker's Guide to the Galaxy." },
    {
      role: "user",
      content: "Explain quantum computing for me, assuming professional level understand from my end",
    },
  ],
});

console.log(completion.choices[0].message);