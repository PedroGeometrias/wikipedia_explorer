# Wikipedia Explorer
This project was made to learn some webassembly and also to train my database skills a little bit more, 
I collect a bunch of data from MediaWiki API, I then store them in PostgreSQL as crawl snapshots. 
In the Browser part I use javascript to render the nodes (Three.js/WebGl), 
and C graph algorithms to interact with said nodes, I don't use embeddings, and there
is no Machine learning happening, you can see some clusters forming though, 
because NetworkX detects communities based on which articles are densely connected. The force-directed layout also pulls linked nodes closer together. 
I also updated the UI, you can search for articles, find a random one, navigate using a C stack data structure (going forward and backwards), also, 
I link the current focused article, so you can go and read it for your self, I consider the projec complete now.
# How to check it out
I exported a small dataset so the project can run entirely in the browser and be hosted on GitHub Pages. 
The graph algorithms are written in C and compiled to WebAssembly.

[Open Wikipedia Explorer](https://pedrogeometrias.github.io/wikipedia_explorer/)

