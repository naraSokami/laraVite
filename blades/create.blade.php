@extends('layouts/back')

@section('content')
    <div class="container mt-4">

        @if ($errors->any())
            <div class="alert alert-danger">
                <ul>
                    @foreach ($errors->all() as $error)
                        <li>{{ $error }}</li>
                    @endforeach
                </ul>
            </div>
        @endif
 
        <div class="row">
            {{-- toReplace --}}
                <button type=submit class="btn btn-info">Submit</button>
            </form>
        </div>
    </div>
@endsection