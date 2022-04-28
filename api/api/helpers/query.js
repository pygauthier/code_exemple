const { PaginationParameters } = require('mongoose-paginate-v2');
const mongoosePaginate = require('mongoose-paginate-v2');

/*
https://github.com/aravindnc/mongoose-paginate-v2
Parameters
[query] {Object} - Query criteria. Documentation
[options] {Object}
    [select] {Object | String} - Fields to return (by default returns all fields). Documentation
    [collation] {Object} - Specify the collation Documentation
    [sort] {Object | String} - Sort order. Documentation
    [populate] {Array | Object | String} - Paths which should be populated with other documents. Documentation
    [projection] {String | Object} - Get/set the query projection. Documentation
    [lean=false] {Boolean} - Should return plain javascript objects instead of Mongoose documents? Documentation
    [leanWithId=true] {Boolean} - If lean and leanWithId are true, adds id field with string representation of _id to every document
    [offset=0] {Number} - Use offset or page to set skip position
    [page=1] {Number}
    [limit=10] {Number}
    [customLabels] {Object} - Developers can provide custom labels for manipulating the response data.
    [pagination] {Boolean} - If pagination is set to false, it will return all docs without adding limit condition. (Default: True)
    [useEstimatedCount] {Boolean} - Enable estimatedDocumentCount for larger datasets. Does not count based on given query, so the count will match entire collection size. (Default: False)
    [useCustomCountFn] {Boolean} - Enable custom function for count datasets. (Default: False)
    [forceCountFn] {Boolean} - Set this to true, if you need to support $geo queries. (Default: False)
    [allowDiskUse] {Boolean} - Set this to true, which allows the MongoDB server to use more than 100 MB for query. This option can let you work around QueryExceededMemoryLimitNoDiskUseAllowed errors from the MongoDB server. (Default: False)
    [read] {Object} - Determines the MongoDB nodes from which to read. Below are the available options.
    [pref]: One of the listed preference options or aliases.
    [tags]: Optional tags for this query. (Must be used with [pref])
    [options] {Object} - Options passed to Mongoose's find() function. Documentation

exemple url:
?identifications.aq=test_aq_32&page=1&limit=1&select=sap version id, identifications.aq

Populate use case:
N.B. ne fonctionne pas sur un call /:id/
?populate=created_by&populate=updated_by&populate=category

{
    "items": [
        {
            "_id": "622f88bccf8d39b6e2aa4e07",
            "version": 2,
            "sap": "test3",
            "identifications": {
                "aq": "test_aq_32"
            },
            "id": "622f88bccf8d39b6e2aa4e07"
        }
    ],
    "totalDocs": 1,
    "limit": 1,
    "totalPages": 1,
    "page": 1,
    "pagingCounter": 1,
    "hasPrevPage": false,
    "hasNextPage": false,
    "prev": null,
    "next": null
}
*/

mongoosePaginate.paginate.options = {
    lean: true,
    limit: 20,
    customLabels: {
        docs: 'items',
        nextPage: 'next',
        prevPage: 'prev',
    },
};

exports.set = request => {
    const params = new PaginationParameters(request).get();
    const query = {};
    Object.keys(request.query).forEach(key => {
        if (!Object.keys(params[1]).includes(key)) {
            if (key.includes('__')) {
                const newKey = key.split('__');
                query[newKey[0]] = {};
                let value = request.query[key];
                if (typeof value === 'string') {
                    value = value.replace(/'/g, '"');
                }
                query[newKey[0]][`$${newKey[1]}`] = JSON.parse(value);
            } else {
                query[key] = request.query[key];
            }
        }
    });
    return [query, params[1]];
};
