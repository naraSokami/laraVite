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

        @if (session()->has('success'))
            <ul class="alert alert-success ps-5">
                <li>{{ session('success') }}</li>
            </ul>
        @endif

        @if (session()->has('fail'))
            <ul class="alert alert-danger ps-5">
                <li>{{ session('fail') }}</li>
            </ul>
        @endif
 
        <div class="row">
            <form action="{{ route("__name__.send") }}" method="POST" enctype="multipart/form-data">
                @csrf
                <div class="mb-3 col-12 col-md-6">
					<label for="subject" class="form-label">Subject</label>
					<input type=text class="form-control" id="subject" name="subject">
				</div>
                <div class="mb-3 col-12 col-md-6">
                    <label for="content" class="form-label">Content</label>
                    <textarea class="form-control" id="content" name="content"></textarea>
                </div>
                <button type="submit" class="btn btn-info">Send</button>
            </form>
        </div>
    </div>
@endsection