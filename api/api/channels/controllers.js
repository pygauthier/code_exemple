const Filters = require('../helpers/query');
const Channel = require('./models/Channel');

exports.getChannels = (request, response) => {
    Channel.paginate(...Filters.set(request))
        .then(data => {
            response.status(200).json(data);
        })
        .catch(error => {
            response.status(404).json(error);
        });
};

exports.getChannel = (request, response) => {
    Channel.findById(request.params.id)
        .then(data => {
            response.status(200).json(data);
        })
        .catch(error => {
            response.status(404).json(error);
        });
};

exports.createChannel = (request, response) => {
    new Channel(request.body)
        .save()
        .then(data => {
            response.status(200).json(data);
        })
        .catch(error => {
            response.status(404).json(error);
        });
};

exports.updateChannel = (request, response) => {
    const code = request.params.id;
    Channel.findOneAndUpdate({ _id: code }, request.body)
        .then(data => {
            response.status(200).json(data);
        })
        .catch(error => {
            response.status(404).json(error);
        });
};

exports.deleteChannel = (request, response) => {
    const code = request.params.id;
    Channel.findOneAndDelete({ _id: code })
        .then(data => {
            response.status(200).json(data);
        })
        .catch(error => {
            response.status(404).json(error);
        });
};
