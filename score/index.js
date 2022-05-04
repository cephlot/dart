const express = require('express')
const app = express()
const port = 3000
var bodyParser = require('body-parser');
const http = require('http');
const io = require('socket.io')(http);
var server = http.createServer(app);

let obj = {p1_score: 0, p2_score: 0}
var clients = [];

io.listen(server);

app.set('view engine', 'pug')
app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ 
	extended: true 
 }));

 io.sockets.on('connect', function() {
    clients.push(io.sockets);
	io.emit('data', obj);
    console.log("connected");
});

//Send data every second.
setInterval(function() {
	io.emit('data', obj);
}, 1000);

app.get('/', (_req, res) => {
    res.render('index', obj)
})

app.put('/', (req, res) => {
    obj = req.body

	res.render('index', obj)
})

app.post('/', (req, res) => {
    obj = req.body

	console.log(req.body)

	res.render('index', obj)
})

app.delete('/', (_req, res) => {
	obj = {1: 0, 2: 0};

	res.render('index', obj)
})

server.listen(port, () => {
  console.log(`Example app listening on port ${port}`)
})