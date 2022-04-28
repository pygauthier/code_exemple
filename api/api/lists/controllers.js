const Filters = require('../helpers/query');
const List = require('./models/lists');

exports.getLists = async (request, response) => {
    try {
        if (request.query.populate === undefined) {
            request.query = {
                ...request.query,
                populate: 'items',
            };
        }
        const lists = await List.paginate(...Filters.set(request));
        lists.items.forEach(list => {
            const reducedItems = [];
            const scoreArray = [];
            list.items.forEach(item => {
                scoreArray.push(item.score);
                reducedItems.push({
                    _id: item._id,
                    sap: item.sap,
                    names: item.names,
                    score: item.score,
                });
            });
            const sum = scoreArray.reduce((a, b) => a + b, 0);
            const avg = sum / scoreArray.length || 0;
            list.score = avg;
            list.items = reducedItems;
        });
        response.status(200).json(lists);
    } catch (error) {
        console.log(error);
        response.status(404).json(error);
    }
};

exports.getList = (request, response) => {
    List.findById(request.params.id)
        .populate('items')
        .then(data => {
            const scoreArray = [];
            data.items.forEach(item => scoreArray.push(item.score));
            const sum = scoreArray.reduce((a, b) => a + b, 0);
            const avg = sum / scoreArray.length || 0;
            data.score = avg;
            response.status(200).json({ ...data._doc, score: avg });
        })
        .catch(error => {
            response.status(404).json(error);
        });
};

exports.createList = (request, response) => {
    new List(request.body)
        .save()
        .then(data => {
            response.status(200).json(data);
        })
        .catch(error => {
            response.status(404).json(error);
        });
};

exports.updateList = (request, response) => {
    const code = request.params.id;
    List.findOneAndUpdate({ _id: code }, request.body)
        .then(data => {
            response.status(200).json(data);
        })
        .catch(error => {
            response.status(404).json(error);
        });
};

exports.deleteList = (request, response) => {
    const code = request.params.id;
    List.findOneAndDelete({ _id: code })
        .then(data => {
            response.status(200).json(data);
        })
        .catch(error => {
            response.status(404).json(error);
        });
};
