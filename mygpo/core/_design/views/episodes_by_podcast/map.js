function(doc)
{
    if(doc.doc_type == "Episode")
    {
        emit(doc.podcast, null);
    }
}
