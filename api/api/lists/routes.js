const express = require('express');

const isAuth = require('../middleware/isAuth');

const router = express.Router();
const listController = require('./controllers');

router.get('/', isAuth, listController.getLists);
router.get('/:id', isAuth, listController.getList);
router.post('/', isAuth, listController.createList);
router.patch('/:id', isAuth, listController.updateList);
router.delete('/:id', isAuth, listController.deleteList);

module.exports = router;
