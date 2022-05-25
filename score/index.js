const express = require('express')
const app = express()
const port = 3000
var bodyParser = require('body-parser');
const http = require('http');
const io = require('socket.io')(http);
var server = http.createServer(app);
var path = require('path');
const sharp = require('sharp');
const fs = require('fs');

sharp.cache(false);

var clients = [];

var current_image = 'public/combined' + new Date().getTime() + '.jpg'

let obj = {player_scores: [301, 301, 301, 301], current_player: 0, image: current_image}

io.listen(server);

app.set('view engine', 'pug')
app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ 
	extended: true 
 }));

 app.use("/public", express.static(path.join(__dirname, 'public')));

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
	obj = {player_scores: [301, 301, 301, 301], current_player: 0, image: '/public/ref.jpg'};

	res.render('index', obj)
})

app.post('/coord', (req, res) => {
	var new_image = 'public/combined' + new Date().getTime() + '.jpg';

	console.log('current ', current_image);
	console.log('new ', new_image);

	sharp('public/marker.png')
		.resize(50, 50)
		.toBuffer({ resolveWithObject: true })
		.then(({data, info}) => {
			sharp(current_image)
				.composite([{
					input: data,
					left: 50, 
					top: 50,
			}])
		.toBuffer(function(err, buffer) {
			fs.writeFile(new_image, buffer, function(e) {});
			fs.unlinkSync(current_image);
			current_image = new_image;
			obj.image = current_image;
			res.render('index', obj)
		});
	})
})

app.delete('/coord', (_req, res) => {
	obj = {player_scores: [301, 301, 301, 301], current_player: 0, image: '/public/ref.jpg'};

	res.render('index', obj)
})

server.listen(port, () => {
  sharp('public/ref.jpg')
	  .toBuffer(function(err, buffer) {
		fs.writeFile(current_image, buffer, function(e) {});
	  });

  console.log(`Example app listening on port ${port}`)
})