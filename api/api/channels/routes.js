const express = require('express');

const isAuth = require('../middleware/isAuth');

const router = express.Router();
const channelController = require('./controllers');

router.get('/', isAuth, channelController.getChannels);
router.get('/:id', isAuth, channelController.getChannel);
router.post('/', isAuth, channelController.createChannel);
router.patch('/:id', isAuth, channelController.updateChannel);
router.delete('/:id', isAuth, channelController.deleteChannel);

module.exports = router;
