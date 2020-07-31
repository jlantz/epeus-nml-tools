import colander
import deform
import os
from lxml import etree
from pyramid.httpexceptions import HTTPFound
from pyramid.view import view_config
from pyramid_deform import SessionFileUploadTempStore
from epeus_nml_tools.util.playlist_report import UnplayedPlaylist


@colander.deferred
def upload_widget(node, kw):
    request = kw["request"]
    tmpstore = SessionFileUploadTempStore(request)
    return deform.widget.FileUploadWidget(tmpstore)


@colander.deferred
def deferred_choices_widget(node, kw):
    playlists = kw.get("playlists")
    playlists = [(playlist, playlist) for playlist in playlists]
    return deform.widget.SelectWidget(multiple=True, values=playlists, size=10)


class CollectionFile(colander.MappingSchema):
    file = colander.SchemaNode(deform.schema.FileData(), widget=upload_widget,)


class UnplayedPlaylistConfig(colander.MappingSchema):
    name = colander.SchemaNode(colander.String(), default="Unplayed", required=True)
    search_playlists = colander.SchemaNode(
        colander.Set(),
        description="Select the playlists to select entries from",
        widget=deferred_choices_widget,
        required=True,
    )
    exclude_playlists = colander.SchemaNode(
        colander.Set(),
        description="Select the playlists to exclude entries from",
        widget=deferred_choices_widget,
        required=True,
    )


@view_config(route_name="home", renderer="../templates/upload_collection.jinja2")
def upload_collection(request):
    collection = get_collection_from_session(request)
    redirect_path = "/unplayed"
    if collection:
        return HTTPFound(location=redirect_path)
    schema = CollectionFile().bind(request=request)
    form = deform.Form(schema, buttons=("submit",))
    template_values = {}
    template_values.update(form.get_widget_resources())

    if "submit" in request.POST:
        controls = request.POST.items()
        try:
            form.validate(controls)
        except deform.ValidationFailure as e:
            template_values["form"] = e.render()
        else:
            return HTTPFound(location=redirect_path)
        return template_values

    template_values["form"] = form.render()
    return template_values


@view_config(route_name="unplayed", renderer="../templates/unplayed_playlist.jinja2")
def unplayed_playlist(request):
    collection = get_collection_from_session(request)
    if not collection:
        return HTTPFound(location="/")
    schema = UnplayedPlaylistConfig().bind(playlists=collection.get_playlists())

    form = deform.Form(schema, buttons=("submit",))
    template_values = {}
    template_values.update(form.get_widget_resources())

    if "submit" in request.POST:
        controls = request.POST.items()
        try:
            values = form.validate(controls)
        except deform.ValidationFailure as e:
            raise e
            template_values["form"] = e.render()
        else:
            request.session.update(values)
        return template_values

    template_values["form"] = form.render()
    return template_values


@view_config(route_name="download_unplayed")
def download_unplayed(request):
    collection = get_collection_from_session(request)
    collection.get_diff(
        request.session["search_playlists"], request.session["exclude_playlists"],
    )
    name = request.session["name"]
    playlist = collection.create_playlist(name)
    request.response.content_disposition = f"attachment;filename={name}.nml"
    request.response.content_type = "application/nml"
    request.response.body = etree.tostring(playlist, pretty_print=True)
    request.response.set_cookie("download_complete", value=name, max_age=10)

    return request.response


def get_collection_from_session(request):
    if "substanced.tempstore" not in request.session:
        return
    if len(request.session["substanced.tempstore"]) == 0:
        return
    path = (
        "/tmp/deform_temp/"
        + list(request.session["substanced.tempstore"].values())[0]["randid"]
    )
    if os.path.isfile(path):
        collection = UnplayedPlaylist(path)
        return collection
