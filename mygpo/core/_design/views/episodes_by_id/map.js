function(doc)
{
    if(doc.doc_type == "Episode")
    {
        emit(doc._id, null);
    }
}
