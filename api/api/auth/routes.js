const express = require('express');

const isAuth = require('../middleware/isAuth');

const router = express.Router();
const authController = require('./controllers');

router.get('/current', isAuth, authController.getUser);
router.post('/login', authController.postLoginUser);
router.post('/login/intranet', authController.postIntranetLogin);
router.post('/user', authController.postCreateUser);

router.get('/tokens', authController.getToken);
router.post('/tokens', authController.postCreateToken);

module.exports = router;
