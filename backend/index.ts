import { env } from "bun";
import express from "express";
import { tavily } from '@tavily/core';

const app = express();
const port = 3000;
const client = tavily({ apiKey: env.TAVILY_API_KEY });

app.get("/", async (req, res) => {     
    try {
        const response = await client.search("what is deep learning", {
            searchDepth: "advanced"
        });
        res.send(response);
        console.log(response);
    } catch (error) {
        res.status(500).send({ error: error.message });
    }
});

app.listen(port, () => {
    console.log(`Listening on port ${port}...`);
});