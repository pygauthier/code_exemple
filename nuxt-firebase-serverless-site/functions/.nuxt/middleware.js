const middleware = {}

middleware['auth'] = require('../../src/middleware/auth.js')
middleware['auth'] = middleware['auth'].default || middleware['auth']

export default middleware
