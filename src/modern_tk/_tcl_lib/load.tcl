fconfigure stdout -buffering none -translation binary
fconfigure stdin -translation binary

package require Tk

set auto_path [linsert $auto_path 0 [
    file dirname [info script]
]]

package require msgpack

proc windowDestroyed {w} {
    set p [msgpack::packer new]
    $p pack array 2
    $p pack str "windowDestroyed"
    $p pack str $w
    puts -nonewline [$p data]
}

bind . <Destroy> {windowDestroyed .}

proc callback {cid args} {
    set p [msgpack::packer new]
    $p pack array 3
    $p pack str "callback"
    $p pack str $cid
    $p pack list str $args
    puts -nonewline [$p data]
}

proc doTcl {id code} {
    set p [msgpack::packer new]
    $p pack array 4
    $p pack str "result"
    $p pack uint32 $id
    catch $code result errorData
    set retCode [dict get $errorData -code]
    $p pack uint8 $retCode
    if {$retCode > 0} {
        set error [dict create]
        dict set error info [dict get $errorData -errorinfo]
        dict set error code [dict get $errorData -errorcode]
        $p pack dict str str $error
    } else {
        $p pack str $result
    }
    puts -nonewline [$p data]
}
